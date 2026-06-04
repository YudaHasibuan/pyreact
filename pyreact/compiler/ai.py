"""AI-Assisted Development Integration for PyReact.
Uses free local Ollama server, with a high-fidelity template generator fallback.
"""
import urllib.request
import json
import re

def call_local_llm(prompt: str, system_prompt: str = "") -> str:
    """Calls local Ollama API for free offline inference.
    If offline, raises ConnectionError.
    """
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "llama3",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("response", "").strip()
    except Exception as e:
        raise ConnectionError(
            "Ollama offline. Start Ollama locally with: 'ollama run llama3'"
        )

def generate_ai_code(prompt: str) -> str:
    """Generates PyReact code using local Ollama if available,
    otherwise falls back to generating a responsive template using local heuristics.
    """
    system_prompt = (
        "You are an expert PyReact code generator. Generate ONLY valid PyReact code "
        "comprising blocks like shared_state, server, database, and components. "
        "Do not write markdown formatting or explanations outside the code block."
    )
    
    try:
        # Try utilizing local free LLM
        return call_local_llm(prompt, system_prompt)
    except ConnectionError:
        # High-fidelity fallback template generation based on keywords
        prompt_lower = prompt.lower()
        
        if "dashboard" in prompt_lower or "analytics" in prompt_lower:
            return """# Auto-scaffolded AI Dashboard
shared_state {
    selected_metric = "users"
    refresh_count = 0
}

server {
    def get_analytics():
        return {
            "users": [
                {"label": "Jan", "value": 120},
                {"label": "Feb", "value": 240},
                {"label": "Mar", "value": 350}
            ],
            "sales": [
                {"label": "Jan", "value": 850},
                {"label": "Feb", "value": 1900},
                {"label": "Mar", "value": 2400}
            ]
        }
}

component Dashboard():
    metrics, setMetrics = use_state(None)
    
    def load_metrics():
        data = server.get_analytics()
        setMetrics(data)
        shared.refresh_count += 1
        
    return (
        <UI.Page>
            <UI.Navbar title="AI Analytics Dashboard" />
            <div className="pt-24 max-w-6xl mx-auto px-4">
                <UI.Heading>Analytics Dashboard</UI.Heading>
                <UI.Text>Generated locally and for free using PyReact Copilot.</UI.Text>
                
                <div className="grid md:grid-cols-3 gap-6 mt-8">
                    <UI.Card title="Controls">
                        <UI.Button onClick={load_metrics}>Load Analytics</UI.Button>
                        <UI.Text className="mt-2 text-xs">Refresh count: {shared.refresh_count}</UI.Text>
                    </UI.Card>
                    
                    <UI.Card title="User Metrics">
                        <UI.Text>Monitor and track active users.</UI.Text>
                    </UI.Card>
                    
                    <UI.Card title="Revenue Stream">
                        <UI.Text>Realtime billing stats.</UI.Text>
                    </UI.Card>
                </div>
            </div>
        </UI.Page>
    )
"""
        
        elif "form" in prompt_lower or "input" in prompt_lower or "login" in prompt_lower:
            return """# Auto-scaffolded AI Form Component
server {
    def submit_feedback(name, email, feedback):
        # Database or email trigger mock
        return {"status": "success", "message": f"Thank you {name}, we received your feedback!"}
}

component FeedbackForm():
    name, setName = use_state("")
    email, setEmail = use_state("")
    feedback, setFeedback = use_state("")
    status, setStatus = use_state(None)
    
    def handle_submit():
        res = server.submit_feedback(name, email, feedback)
        setStatus(res.get("message"))
        setName("")
        setEmail("")
        setFeedback("")
        
    return (
        <UI.Page>
            <UI.Navbar title="AI Feedback Form" />
            <div className="pt-24 max-w-md mx-auto px-4">
                <UI.Card title="Submit Feedback">
                    <UI.Input label="Name" value={name} onChange={setName} placeholder="Enter your name" />
                    <UI.Input label="Email" value={email} onChange={setEmail} placeholder="Enter your email" />
                    <UI.Input label="Feedback" value={feedback} onChange={setFeedback} placeholder="Your comments..." />
                    
                    <div className="mt-4">
                        <UI.Button onClick={handle_submit}>Submit</UI.Button>
                    </div>
                    
                    {status && (
                        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-lg text-sm">
                            {status}
                        </div>
                    )}
                </UI.Card>
            </div>
        </UI.Page>
    )
"""

        # General component fallback
        return """# Auto-scaffolded AI General Component
component HelloAI():
    return (
        <UI.Page>
            <UI.Navbar title="AI Hello World" />
            <div className="pt-24 text-center max-w-xl mx-auto px-4">
                <UI.Heading>Hello from PyReact AI</UI.Heading>
                <UI.Text>This UI block was generated locally by the PyReact AI Assistant.</UI.Text>
            </div>
        </UI.Page>
    )
"""
