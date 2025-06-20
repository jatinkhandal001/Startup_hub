import gradio as gr
import os
import random
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import requests
from bs4 import BeautifulSoup
import threading
import time
import logging
from functools import wraps, lru_cache
from openai import OpenAI

# Setup basic logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# API Keys
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Decorators

def log_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Exception in {func.__name__}: {e}", exc_info=True)
            return f"An error occurred in {func.__name__}: {e}"
    return wrapper

def validate_nonempty(func):
    @wraps(func)
    def wrapper(text):
        if not text or not text.strip():
            return "Input cannot be empty."
        return func(text)
    return wrapper

def retry(times=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Attempt {attempt} failed in {func.__name__}: {e}")
                    if attempt == times:
                        return f"Failed after {times} attempts: {e}"
                    time.sleep(delay)
        return wrapper
    return decorator

# Functions

@log_exceptions
@validate_nonempty
@lru_cache(maxsize=128)
def search_startup(query):
    try:
        from serpapi import GoogleSearch
    except ImportError:
        return "SerpAPI not installed. Run: pip install google-search-results"

    if not SERPAPI_KEY or SERPAPI_KEY == "YOUR_API_KEY":
        return "Please set your SerpAPI key as the SERPAPI_KEY variable."

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
    except Exception as e:
        return f"Error: {e}"

    result_text = f"Search results for: {query}\n\n"
    if "organic_results" in results:
        for i, result in enumerate(results.get("organic_results", []), start=1):
            title = result.get("title", "No Title")
            snippet = result.get("snippet", "No Description Available.")
            link = result.get("link", "No Link")
            result_text += f"{i}. {title}\n   {snippet}\n   🔗 {link}\n\n"
    else:
        result_text += "No results found or invalid API key."
    return result_text


@log_exceptions
@validate_nonempty
def startup_health_dashboard(startup):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    growth = [random.randint(1000, 5000)]
    for _ in range(5):
        growth.append(max(500, growth[-1] + random.randint(-500, 1000)))

    funding = random.randint(1, 5)
    sentiment = round(random.uniform(2.0, 5.0), 2)
    team = max(1, 5 - random.randint(0, 4))
    community = round(random.uniform(2.5, 5.0), 2)
    health_score = round(np.mean([growth[-1]/5000, funding, sentiment, team, community]), 2)

    plt.figure(figsize=(7, 4))
    plt.subplot(2, 1, 1)
    plt.plot(months, growth, marker='o', color='dodgerblue')
    plt.title(f"{startup} Growth Trend")
    plt.ylabel("Users/Visits")
    plt.grid(True)

    plt.subplot(2, 1, 2)
    categories = ["Growth", "Funding", "Sentiment", "Team", "Community"]
    scores = [growth[-1]/5000, funding, sentiment, team, community]
    bars = plt.bar(categories, scores, color='skyblue')
    plt.ylim(0, 5)
    plt.ylabel("Score (1-5)")
    plt.title(f"Health Factors - Score: {health_score}/5")
    for bar, value in zip(bars, scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05, f"{value:.2f}", ha='center', va='bottom')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img = Image.open(buf)

    summary = (f"Health Score: {health_score}/5\n"
               f"Funding Rounds: {funding}\n"
               f"Sentiment: {sentiment}/5\n"
               f"Team Stability: {team}/5\n"
               f"Community: {community}/5")
    return summary, img


@log_exceptions
@validate_nonempty
@retry(times=3, delay=3)
def event_finder(query):
    query = query.lower()
    events = []

    try:
        url = 'https://www.meetup.com/find/events/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for event in soup.find_all('h3'):
            title = event.get_text(strip=True)
            if query in title.lower():
                events.append(f"[Meetup] {title}")
        for event in soup.find_all('h2'):
            title = event.get_text(strip=True)
            if query in title.lower():
                events.append(f"[Microsoft] {title}")
    except:
        pass

    try:
        url = 'https://www.techmeme.com/events'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for event in soup.select('div.ourcol div.rhov'):
            title = event.get_text(strip=True)
            if query in title.lower():
                events.append(f"[Techmeme] {title}")
    except:
        pass

    try:
        url = 'https://events.microsoft.com/en-us/'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for event in soup.find_all('h3'):
            title = event.get_text(strip=True)
            if query in title.lower():
                events.append(f"[Microsoft] {title}")
    except:
        pass

    try:
        url = 'https://developers.google.com/events'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for event in soup.find_all('h3'):
            title = event.get_text(strip=True)
            if query in title.lower():
                events.append(f"[Google] {title}")
    except:
        pass

    return "\n".join(events) if events else "No matching events found."


@log_exceptions
@validate_nonempty
def ai_search_startup(myprompt):
    if not GEMINI_API_KEY:
        return "Please configure your Gemini API key."
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    try:
        messages = [
            {"role": "system", "content": "You are a helpful Startup AI assistant. Answer queries related to startups and startup ideas only."},
            {"role": "user", "content": myprompt}
        ]
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages
        )
        if not response.choices or not hasattr(response.choices[0], "message"):
            return "No response from Gemini API."
        return response.choices[0].message.content
    except Exception as e:
        return f"Error while calling AI assistant: {e}"


@log_exceptions
@validate_nonempty
def seo_insights(domain):
    insights = {
        "domain": domain,
        "monthly_visits": random.randint(1000, 50000),
        "bounce_rate": round(random.uniform(20, 70), 2),
        "backlinks": random.randint(100, 5000),
        "domain_authority": random.randint(10, 90)
    }
    return (f"SEO Insights for {domain}:\n"
            f"Monthly Visits: {insights['monthly_visits']}\n"
            f"Bounce Rate: {insights['bounce_rate']}%\n"
            f"Backlinks: {insights['backlinks']}\n"
            f"Domain Authority: {insights['domain_authority']}/100")


@log_exceptions
@validate_nonempty
def idea_validator(idea_text):
    if not GEMINI_API_KEY:
        return "Please configure your Gemini API key."
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    messages = [
        {"role": "system", "content": "You are an expert startup idea validator."},
        {"role": "user", "content": f"Validate this startup idea:\n{idea_text}"}
    ]
    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages
        )
        if not response.choices or not hasattr(response.choices[0], "message"):
            return "No response from Gemini API."
        return response.choices[0].message.content
    except Exception as e:
        return f"Error from Gemini API: {e}"


@log_exceptions
@validate_nonempty
def recommend_tools(keywords):
    if not GEMINI_API_KEY:
        return "Please configure your Gemini API key."
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant recommending startup tools."},
        {"role": "user", "content": f"Recommend tools for these keywords:\n{keywords}"}
    ]
    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages
        )
        if not response.choices or not hasattr(response.choices[0], "message"):
            return "No response from Gemini API."
        return response.choices[0].message.content
    except Exception as e:
        return f"Error from Gemini API: {e}"


# Gradio UI Setup

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="violet")) as demo:
    gr.Markdown("### 🚀 Welcome to Startup Hub by Team Falcon 🦅")

    with gr.Tab("1. Startup Company Search"):
        query = gr.Textbox(label="Search for Startup")
        btn = gr.Button("Search")
        output = gr.Textbox(label="Results", lines=10)
        btn.click(search_startup, inputs=[query], outputs=[output])

    with gr.Tab("2. Startup Health Checkup & Growth"):
        name = gr.Textbox(label="Startup Name")
        run_btn = gr.Button("Run Checkup")
        summary = gr.Textbox(label="Summary", lines=5)
        chart = gr.Image(label="Health Chart")
        run_btn.click(startup_health_dashboard, inputs=[name], outputs=[summary, chart])

    with gr.Tab("3. Event Finder"):
        event_input = gr.Textbox(label="Topic (e.g. AI, Microsoft)")
        event_btn = gr.Button("Find Events")
        event_output = gr.Textbox(label="Event Results", lines=10)
        event_btn.click(event_finder, inputs=[event_input], outputs=[event_output])

    with gr.Tab("4. AI Assistant"):
        prompt = gr.Textbox(label="Ask AI Assistant")
        ask_btn = gr.Button("Ask")
        answer = gr.Markdown()
        ask_btn.click(ai_search_startup, inputs=[prompt], outputs=[answer])

    with gr.Tab("5. Traffic & SEO Insights"):
        domain = gr.Textbox(label="Enter Domain")
        seo_btn = gr.Button("Get SEO")
        seo_out = gr.Textbox(label="SEO Report", lines=7)
        seo_btn.click(seo_insights, inputs=[domain], outputs=[seo_out])

    with gr.Tab("6. Startup Idea Validator"):
        idea = gr.Textbox(label="Your Startup Idea")
        idea_btn = gr.Button("Validate")
        idea_out = gr.Textbox(label="Validation", lines=10)
        idea_btn.click(idea_validator, inputs=[idea], outputs=[idea_out])

    with gr.Tab("7. Startup Tool Recommender"):
        keyword = gr.Textbox(label="Keywords")
        tools_btn = gr.Button("Get Tools")
        tools_out = gr.Textbox(label="Tools", lines=7)
        tools_btn.click(recommend_tools, inputs=[keyword], outputs=[tools_out])


# Self-ping thread to keep Render app awake
def keep_awake():
    while True:
        try:
            print("[PING] Keeping the app awake...")
            requests.get("https://startup-hub.onrender.com")
        except Exception as e:
            print("[ERROR] Ping failed:", e)
        time.sleep(600)  # Ping every 10 minutes

threading.Thread(target=keep_awake, daemon=True).start()

# Launch Gradio app
demo.launch(server_name="0.0.0.0", server_port=7860)
