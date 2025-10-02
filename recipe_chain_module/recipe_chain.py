from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain, SequentialChain
import warnings

# Suppress all warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_recipe_chain(model_name: str = "gpt-4o", temperature: float = 0.2):
    """
    Initializes and returns a SequentialChain that generates recipes
    from grocery offers and compiles a shopping list.

    Args:
        model_name (str): OpenAI model name.
        temperature (float): LLM temperature.

    Returns:
        function: A function that can be called with offers_text to get recipes and shopping list.
    """
    llm = ChatOpenAI(model=model_name, temperature=temperature, openai_api_key=OPENAI_API_KEY)

    recipe_prompt = ChatPromptTemplate.from_template("""
                                        
        You are a helpful cooking assistant.
        You receive a list of grocery offers and their prices from a local supermarket. It looks like this:

        {offers}

        Using **only** the ingredients or appropriate transformations of the ingredients. You may add common pantry items 
        like salt, pepper, oil, rice, potatoes, pasta. 

        Your task is to generate **three distinct recipes**.
        For each recipe, provide:

        - Recipe name
        - Ingredients (with quantities in grams, liters, or pieces)
        - Step-by-step cooking instructions

        Output in a structured way:

        Recipe 1: ...
        Ingredients:
        -...
        Instructions:
        1. ...
        2. ...

        Recipe 2: ...
        ... etc.
        """
    )
    chain_recipes = LLMChain(
        llm=llm,
        prompt=recipe_prompt,
        output_key="recipes",
        verbose=True
    )

    # Chain B, from recipes to shopping list
    shopping_list_prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful assistant.
        You receive **three recipes** in the following structured format:

        {recipes}

        Your task is to generate a **compiled shopping list** of all ingredients needed for the three recipes.
        Combine duplicates (e.g. if "tomatoes" appear in multiple recipes, sum the quantities).
        List each ingredient and the total quantity (with units) needed.
        
        Output **only** the shopping list, one ingredient per line, in a readable format"""

    )

    chain_shopping_list = LLMChain(
        llm=llm,
        prompt=shopping_list_prompt,
        output_key="shopping_list",
        verbose=True
    )

    # Sequential chain
    overall_chain = SequentialChain(
        chains=[chain_recipes, chain_shopping_list],
        input_variables=["offers"],
        output_variables=["recipes", "shopping_list"],
        verbose=True
    )

    def run_chain(offers_text: str):
        return overall_chain.invoke({"offers": offers_text})
    
    return run_chain