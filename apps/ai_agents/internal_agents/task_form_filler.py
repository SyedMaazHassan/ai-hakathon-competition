from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.googlesearch import GoogleSearchTools

class TaskFormFillerAgent:
    def __init__(self, task, response_model, knowledge_base):
        self.task = task
        self.agent = Agent(
            # knowledge=knowledge_base,
            search_knowledge=True,
            name="FormFiller",
            role="You are a task form filler agent that helps users fill out forms by extracting relevant information from given knowledge.",
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=[
                "You are a highly focused task form filler AI agent.",
                "Use the provided knowledge to fill out each form field with the most relevant, concise, and complete data.",
                "Prioritize internal knowledge first. If it's insufficient, use DuckDuckGo to gather more information."            
            ],
            tools=[GoogleSearchTools()],
            response_model=response_model,
            debug_mode=True
        )

    def run(self) -> dict:
        task_name = self.task.name
        task_description = self.task.display_description or self.task.description
        context = f"Task Name: {task_name}\nTask Description: {task_description}"

        filled_output = self.agent.run(
            "Fill the form with the provided knowledge, use Google search if you don't get much info from knowledge",
            context=context
        )


        try:
            output = filled_output.content.dict()
        except Exception:
            output = {"output": str(filled_output.content) if filled_output.content else ""}
        
        return output

