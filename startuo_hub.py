import gradio as gr
import random
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image
import requests
from bs4 import BeautifulSoup

SERPAPI_KEY = "6f86754981d8fb339eb0f3854ab2e53135763066228cae0d91dd71a1f3b054ab"

def search_startup(query):
    try:
        from serpapi import GoogleSearch
    except ImportError:
        return "SerpAPI not installed. Run: pip install google-search-results"

    api_key = SERPAPI_KEY
    if not api_key or api_key == "YOUR_API_KEY":
        return (
            "Please set your SerpAPI key as the SERPAPI_KEY variable at the top of the script to use this feature."
        )
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
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

def startup_health_dashboard(startup):
    if not startup.strip():
        return "Please enter a valid startup name.", None

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

#Web Scrap used in this
def event_finder(query):
    query = query.lower()
    events = []

    #Meetup
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

    # Techmeme
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

    #Microsoft
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

    #Google
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

def ai_search_startup(myprompt):
    from openai import OpenAI
    google_gemini_api_key = "AIzaSyALWY56WD0gzykmToNHlZbxEXYcCw1Mr_A"
    client = OpenAI(
        api_key=google_gemini_api_key,
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
        return response.choices[0].message.content
    except Exception as e:
        return f"Error while calling AI assistant: {e}"

    return f"AI Assistant feature is not configured. Your query was:\n\n{myprompt}"


with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="violet")) as demo:
    gr.Markdown("""<div style="text-align:center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width:1000px; margin:auto;">
        <h1 style="color:#0984e3; font-weight: 900; font-size: 3.2rem; margin-bottom: 0.2rem; text-shadow: 2px 2px 6px rgba(0,0,0,0.1);">Welcome to Your Startup Hub</h1>
        <p style="color:#636e72; font-size: 1.3rem; margin-top: 0; margin-bottom: 1.5rem; line-height: 1.6;">
            A smart, easy-to-use platform to search startups, check health metrics, find events — all in one place.
            Let our AI Startup assistant help you anytime 
        </p>
        <hr style="width:60px; border:3px solid #00cec9; margin: 20px auto 30px;">
        <p style="color:#0984e3; font-weight: 600; font-size: 1rem; margin-top: 0;">
            Developed by <span style="font-weight: 1000;">Team Falcon</span> 🦅
        </p>
    </div>""",
    elem_id="header")

    gr.Markdown("Built with Gemini AI • Serp api key • Web Scrap • Gradio UI • BeautifulSoup")

    with gr.Tab("1. Startup Company Search"):
        gr.Markdown("### Search for any startup or topic to see Google results ")
        search_query = gr.Textbox(label="Search for Startup", placeholder="e.g. fintech startup India")
        search_btn = gr.Button("Search")
        search_output = gr.Textbox(label="Search Results", lines=10)
        search_btn.click(search_startup, inputs=[search_query], outputs=[search_output])

    with gr.Tab("2. Startup Health Checkup & Growth"):
        gr.Markdown("### Get a simulated health checkup and growth dashboard for any startup.")
        health_name = gr.Textbox(label="Enter Startup Name", placeholder="e.g. MyStartup")
        health_btn = gr.Button("Run Health Checkup")
        health_summary = gr.Textbox(label="Health Summary", lines=5)
        health_plot = gr.Image(label="Health Dashboard", format="png")
        health_btn.click(startup_health_dashboard, inputs=[health_name], outputs=[health_summary, health_plot])

    with gr.Tab("3. Event Finder"):
        gr.Markdown("### Find upcoming events from real web sources: Microsoft, Google, Meetup, and Techmeme")
        event_query = gr.Textbox(label="Find Events For", placeholder="e.g. Microsoft, AI,Google,meetup,techmeme")
        event_btn = gr.Button("Find Events")
        event_output = gr.Textbox(label="Event Results", lines=10)
        event_btn.click(event_finder, inputs=[event_query], outputs=[event_output])

    with gr.Tab("4. AI Assistant"):
        gr.Markdown("""
        ### AI Startup Search Assistant  
        Search any startup or topic related with it
        <span style='color:gray'><i>Requires <code> Startup </code> </i></span>
        """)
        with gr.Row():
            with gr.Column():
                user_query = gr.Textbox(label="Search Query", placeholder="e.g. fintech startup India")
                search_btn_ai = gr.Button("Search", variant="primary")
            with gr.Column():
                results = gr.Markdown(label="Results")
        search_btn_ai.click(ai_search_startup, inputs=[user_query], outputs=[results])


    import os
port = int(os.environ.get("PORT", 7860))
demo.launch(server_name="0.0.0.0", server_port=port)




