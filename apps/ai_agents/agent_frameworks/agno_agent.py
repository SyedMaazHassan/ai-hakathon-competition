from agno.agent import Agent as AGAgent, RunResponse
from agno.models.openai import OpenAIChat
from .base_agent import BaseAgent
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.wikipedia import WikipediaTools
from apps.tools.tool_services.chart_tools import ChartTools
from apps.tools.tool_services.pytrend_tools import PyTrendsTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.webbrowser import WebBrowserTools
import time

class AgnoAgent(BaseAgent):
    def get_model(self, model_id: str):
        return OpenAIChat(id=model_id or "gpt-3.5-turbo")

    def set_framework_agent(self):

        self.agent = AGAgent(
            add_context=True,
            telemetry=False,
            model=self.get_model(self.model),
            name=self.name,
            role=self.role,
            description=self.description.full(),
            instructions=self.instructions.full(),
            markdown=True,
            expected_output=self.response_model if (not self.is_structured) else None,
            add_history_to_messages=True,
            num_history_responses=3,
            show_tool_calls=False,
            response_model=self.response_model if (self.is_structured and self.response_model) else None,
            tools=[GoogleSearchTools(), PyTrendsTools(), WikipediaTools(), WebBrowserTools(), ChartTools(), YFinanceTools()],
            knowledge=self.knowledge_base,
            search_knowledge=True,
            debug_mode=True,
            context=self.context
        )


    def run(self, prompt: str, context: str=None) -> dict:
        result: RunResponse = self.agent.run(prompt, context=context)
        try:
            output = result.content.dict() if (self.response_model and self.is_structured) else (result.content or "")
        except Exception:
            output = str(result.content) if result.content else ""
            
        return {
            "content": output,
            "tokens_used": getattr(result, "total_tokens", {}),
        }

    def run_stream(self, prompt: str, context: str=None):
        """
        Enhanced streaming with proper error handling and debugging
        """
        try:
            start_time = time.time()
            
            response_stream = self.agent.run(
                prompt,
                stream=True
            )
            
            chunk_count = 0

            for chunk in response_stream:
             
                chunk_count += 1
                time.time() - start_time

                chunk_output = {
                    'event': chunk.event,
                    'content': chunk.content
                }
                if hasattr(chunk, 'tool'):
                    try:
                        results = chunk.tool.result
                    except:
                        results = chunk.tool.result

                    tool = {
                        'name': chunk.tool.tool_name,
                        'args': chunk.tool.tool_args,
                        'results': results,
                        'is_success': (not chunk.tool.tool_call_error)
                    }
                    chunk_output['tool'] = tool


                yield chunk_output
            

            time.time() - start_time
            
        except Exception as e:
         
            import traceback
            traceback.print_exc()
            
            # Fallback to non-streaming
            try:
                result = self.run(prompt, context=context)
                content = result.get("content", "")
                
                # Simulate streaming by chunking the response
                if content:
                    # Split into reasonable chunks (by sentences or words)
                    sentences = content.split('. ')
                    for i, sentence in enumerate(sentences):
                        if sentence.strip():
                            chunk_content = sentence + ('. ' if i < len(sentences) - 1 else '')
                            yield {"content": chunk_content}
                            time.sleep(0.1)  # Small delay for streaming effect
                            
            except Exception:
                yield {"content": "", "error": str(e)}

    def run_stream_simple(self, prompt: str, context: str=None):
        """
        Simplified streaming version for testing
        """
        try:
            response_stream = self.agent.run(
                prompt,
                stream=True,
                context=context
            )
            
            for chunk in response_stream:
                if chunk.content:
                    yield {"content": chunk.content}
                    
        except Exception as e:
            yield {"content": "", "error": str(e)}
