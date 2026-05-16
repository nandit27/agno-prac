import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Iterator, Union

from agno.workflow import Workflow
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.groq import Groq
from agno.run.agent import RunOutput, RunEvent, RunOutputEvent, RunContentEvent, ToolCallStartedEvent, ToolCallCompletedEvent
from agno.run.workflow import WorkflowRunEvent, WorkflowCompletedEvent, WorkflowRunOutputEvent
from agno.utils.log import logger, set_log_level_to_info

# Load environment variables from .env file
# This will load GROQ_API_KEY into the environment
load_dotenv()

class NewsArticle(BaseModel):
    title: str = Field(..., description='Title of the article.')
    url: str = Field(..., description='URL of the article.')
    summary: Optional[str] = Field(None, description='Summary of the article.')

class SearchResults(BaseModel):
    articles: List[NewsArticle]

class BlogPostGenerator(Workflow):
    searcher = Agent(
        model=Groq(id='llama-3.3-70b-versatile'),
        tools=[DuckDuckGoTools()],
        instructions="Given a topic, search for top 5 articles and return a summary of each with its URL.",
        debug_mode=True
    )

    writer = Agent(
        model=Groq(id='llama-3.3-70b-versatile'),
        instructions="Given a list of articles, write a blog post summarizing the key points.",
        debug_mode=True,
        markdown=True
    )

    def _add_blog_post_to_cache(self, topic: str, blog_post: Optional[str]) -> None:
        logger.info(f"Caching blog post for topic: '{topic}'")

        if self.session_state is None:
            self.session_state = {}
        self.session_state.setdefault("blog_posts", {})
        self.session_state["blog_posts"][topic] = blog_post

        logger.info(f"Blog post cached successfully for topic: '{topic}'")

    def _get_cached_blog_post(self, topic: str) -> Optional[str]:
        logger.info(f"Checking cache for blog post on topic: '{topic}'")

        if self.session_state is None:
            return None
        cached_post = self.session_state.get("blog_posts", {}).get(topic)

        if cached_post:
            logger.info(f"Cache hit for topic: '{topic}'")
        else:
            logger.info(f"No cached blog post found for topic: '{topic}'")

        return cached_post

    def _get_search_results(self, topic: str) -> Iterator[Union[RunOutputEvent, str]]:
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                logger.info(f"Attempt {attempt + 1}: Searching for articles on '{topic}'")
                
                final_content = ""
                # Stream the searcher agent to capture tool calls
                for response in self.searcher.run(topic, stream=True):
                    yield response
                    if isinstance(response, RunContentEvent):
                        if response.content:
                            final_content += response.content

                if final_content:
                    logger.info(f"Found articles on attempt {attempt + 1}")
                    yield final_content
                    return

                logger.warning(f"Attempt {attempt + 1}: Invalid or empty response")
            except Exception as exc:
                logger.warning(f"Attempt {attempt + 1} failed with error: {exc}")

        logger.error(
            f"Failed to retrieve search results for '{topic}' after {max_attempts} attempts"
        )
        yield ""

    def _write_blog_post(
        self,
        topic: str,
        search_results: str,
    ) -> Iterator[RunOutputEvent]:
        logger.info(f"Writing blog post for topic: '{topic}'")

        writer_input = {
            "topic": topic,
            "articles": search_results,
        }

        logger.info(
            "Input prepared for writer agent: "
            f"{json.dumps(writer_input, indent=4)}"
        )

        final_content = ""
        for response in self.writer.run(json.dumps(writer_input, indent=4), stream=True):
            yield response
            if isinstance(response, RunContentEvent):
                if response.content:
                    final_content += response.content

        self._add_blog_post_to_cache(topic, final_content)

    def run(self, topic: str, use_cache: bool = True) -> Iterator[Union[WorkflowRunOutputEvent, RunOutputEvent]]:
        logger.info(f"Generating a blog post on: '{topic}'")
        logger.info(f"use_cache: {use_cache}")

        # Step 1: Check cache
        if use_cache:
            cached_blog_post = self._get_cached_blog_post(topic)
            if cached_blog_post:
                logger.info(f"Using cached blog post for topic: '{topic}'")
                yield WorkflowCompletedEvent(
                    content=cached_blog_post,
                )
                return

        # Step 2: Search for articles
        search_results = ""
        for response in self._get_search_results(topic):
            if isinstance(response, str):
                search_results = response
            else:
                yield response

        if not search_results:
            logger.warning(f"No search results found for topic: '{topic}'")
            yield WorkflowCompletedEvent(
                content=f"No search results found for topic: '{topic}'",
            )
            return

        # Step 3: Write the blog post
        yield from self._write_blog_post(topic, search_results)

if __name__ == "__main__":
    set_log_level_to_info()
    
    generator = BlogPostGenerator()

    print(f"\n--- Generating blog post ' ---\n")
    for response in generator.run(topic="Artificial Intelligence"):
        if isinstance(response, RunContentEvent):
            if response.content:
                print(response.content, end="", flush=True)
        elif hasattr(response, "event") and response.event == RunEvent.tool_call_started:
            tool_name = getattr(response, "tool", None).tool_name if hasattr(response, "tool") and response.tool else "Unknown"
            print(f"\n\n🛠️  Tool Call: {tool_name}")
            tool_args = getattr(response, "tool", None).tool_args if hasattr(response, "tool") and response.tool else None
            if tool_args:
                print(f"   Arguments: {tool_args}")
        elif hasattr(response, "event") and response.event == RunEvent.tool_call_completed:
            tool_name = getattr(response, "tool", None).tool_name if hasattr(response, "tool") and response.tool else "Unknown"
            print(f"✅ Tool Completed: {tool_name}\n")
        elif isinstance(response, WorkflowCompletedEvent):
            print("\n\n--- Workflow Completed ---")
        else:
            logger.debug(f"Received unknown event type: {type(response)}")