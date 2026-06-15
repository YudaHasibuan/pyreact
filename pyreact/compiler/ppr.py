import os
import json
import urllib.request
from pathlib import Path

# Pre-packaged Offline-First Community Library Registry (MIT/Free License)
PPR_REGISTRY = {
    "pyreact-chart": {
        "description": "Premium React Charting library wrapper for PyReact.",
        "files": {
            "chart.pyreact": """# PyReact Charting Package (pyreact-chart)
# Shared state, mock analytics, and visual Chart.js custom wrapping.

shared_state {
    "chart_active_metric": "users",
    "chart_timeframe": "7d"
}

server {
    def get_chart_data(metric: str, timeframe: str):
        # Generates responsive dataset based on parameters
        if metric == "users":
            return [
                {"label": "Mon", "value": 120},
                {"label": "Tue", "value": 150},
                {"label": "Wed", "value": 180},
                {"label": "Thu", "value": 220},
                {"label": "Fri", "value": 260},
                {"label": "Sat", "value": 310},
                {"label": "Sun", "value": 400}
            ]
        else:
            return [
                {"label": "Mon", "value": 1200},
                {"label": "Tue", "value": 1900},
                {"label": "Wed", "value": 3000},
                {"label": "Thu", "value": 5000},
                {"label": "Fri", "value": 6200},
                {"label": "Sat", "value": 7500},
                {"label": "Sun", "value": 9000}
            ]
}

component ChartWrapper() {
    state data = []
    
    def load_chart():
        metrics = server.get_chart_data(shared.chart_active_metric, shared.chart_timeframe)
        set_data(metrics)
        
    on_mount:
        load_chart()
        
    render:
        <UI.Card title="Interactive Chart.js Analytics (PPR Package)">
            <div className="flex gap-2 mb-4 justify-end">
                <button 
                    onClick={() => { setShared("chart_active_metric", "users"); load_chart(); }}
                    className={`px-3 py-1 text-xs rounded-lg ${shared.chart_active_metric === "users" ? "bg-blue-600 text-white" : "bg-white/5 text-white/60"}`}
                >
                    Active Users
                </button>
                <button 
                    onClick={() => { setShared("chart_active_metric", "revenue"); load_chart(); }}
                    className={`px-3 py-1 text-xs rounded-lg ${shared.chart_active_metric === "revenue" ? "bg-blue-600 text-white" : "bg-white/5 text-white/60"}`}
                >
                    Revenue ($)
                </button>
            </div>
            {data.length > 0 ? (
                <UI.Chart type="line" data={data} height={200} />
            ) : (
                <div className="text-white/40 text-center py-10">Loading chart data...</div>
            )}
        </UI.Card>
}
"""
        }
    },
    "pyreact-auth": {
        "description": "Secure user session, credentials authentication, and login UI flow wrapper.",
        "files": {
            "auth.pyreact": """# PyReact Credentials Authentication Package (pyreact-auth)

shared_state {
    "auth_user": None,
    "auth_token": None,
    "auth_checked": False
}

server {
    def login_user(username: str, password_hash: str):
        # Simulates backend authentication
        if username == "admin" and password_hash == "admin123":
            return {"status": "ok", "token": "jwt_token_ppr_auth_2028", "user": {"username": "admin", "role": "Administrator"}}
        return {"status": "error", "message": "Invalid credentials"}
}

component LoginPanel() {
    state username = ""
    state password = ""
    state error_msg = None
    
    def handle_submit():
        res = server.login_user(username, password)
        if res["status"] == "ok":
            setShared("auth_user", res["user"])
            setShared("auth_token", res["token"])
            setShared("auth_checked", True)
        else:
            set_error_msg(res["message"])
            
    render:
        <UI.Card title="Secure Login (PPR Package)">
            <div className="space-y-4">
                <UI.Input 
                    label="Username" 
                    value={username} 
                    onChange={set_username} 
                    placeholder="Enter admin..." 
                />
                <UI.Input 
                    label="Password" 
                    value={password} 
                    onChange={set_password} 
                    placeholder="Enter admin123..." 
                />
                {error_msg && (
                    <div className="text-red-400 text-xs font-semibold">{error_msg}</div>
                )}
                <UI.Button onClick={handle_submit} variant="primary">
                    Sign In
                </UI.Button>
            </div>
        </UI.Card>
}
"""
        }
    },
    "pyreact-theme": {
        "description": "Sleek typography, Outfit font imports, and premium layout presets.",
        "files": {
            "theme.pyreact": """# PyReact Styles & Layout Palette Custom Theme (pyreact-theme)

style {
    primary_color = "#3b82f6"
    bg_dark = "#030712"
    card_bg = "#0f172a"
    accent = "#a855f7"
}

component ThemePreset() {
    render:
        <UI.Page>
            <UI.Navbar title="Sleek Custom Theme Palette" />
            <div className="max-w-4xl mx-auto px-4 py-10 space-y-6">
                <UI.Heading>Outfit Styling Theme Wrapper</UI.Heading>
                <UI.Text>
                    This layout implements custom variable tokens styled natively through variables.css output.
                </UI.Text>
            </div>
        </UI.Page>
}
"""
        }
    }
}

# High-Fidelity Free Templates (SaaS, AI Dashboard, Landing Page)
TEMPLATES = {
    "saas": {
        "description": "Premium SaaS Analytics, users metrics, and billing table UI template.",
        "app.pyreact": """# Premium SaaS Analytics Dashboard Template
# Generated by PyReact Hub / Templates Marketplace (Q4 2028)

shared_state {
    "saas_users_active": 45100,
    "saas_revenue_mrr": 89400,
    "saas_active_tab": "Overview"
}

server {
    def get_users_list():
        return [
            {"id": 1, "name": "Budi Santoso", "email": "budi@nusantara.com", "plan": "Enterprise", "status": "Active"},
            {"id": 2, "name": "Dewi Lestari", "email": "dewi@java.io", "plan": "Pro", "status": "Active"},
            {"id": 3, "name": "Rian Cahyadi", "email": "rian@sumatra.net", "plan": "Free", "status": "Suspended"},
            {"id": 4, "name": "Siti Aminah", "email": "siti@bali.org", "plan": "Pro", "status": "Active"}
        ]
        
    def get_monthly_growth():
        return [
            {"label": "Jan", "value": 15000},
            {"label": "Feb", "value": 24000},
            {"label": "Mar", "value": 35000},
            {"label": "Apr", "value": 48000},
            {"label": "May", "value": 65000},
            {"label": "Jun", "value": 89400}
        ]
}

component App() {
    state users = []
    state growth = []
    state show_success = False
    
    def load_data():
        user_list = server.get_users_list()
        set_users(user_list)
        growth_data = server.get_monthly_growth()
        set_growth(growth_data)
        
    on_mount:
        load_data()
        
    render:
        <UI.Page>
            <UI.Navbar title="SaaS Portal Framework" />
            <div className="pt-24 max-w-6xl mx-auto px-4 pb-16">
                <div className="text-center mb-10">
                    <UI.Heading>SaaS Metric Overview Dashboard</UI.Heading>
                    <UI.Text>Manage active subscriptions, track monthly recurring revenue (MRR), and check real-time user tables.</UI.Text>
                </div>
                
                {/* Stats Row */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    <UI.Card title="Active Accounts Summary">
                        <UI.Text size="lg">Total Subscribers: <strong className="text-blue-400">{shared.saas_users_active} users</strong></UI.Text>
                        <UI.Text color="gray-400" className="mt-2">Growth rates evaluated directly through embedded Flask backend routing.</UI.Text>
                    </UI.Card>
                    <UI.Card title="Financial Performance Overview">
                        <UI.Text size="lg">Current Monthly MRR: <strong className="text-green-400">${shared.saas_revenue_mrr} USD</strong></UI.Text>
                        <UI.Text color="gray-400" className="mt-2">Real-time calculations automatically generated from secure SQLite queries.</UI.Text>
                    </UI.Card>
                </div>
                
                {/* Main Views */}
                <div className="grid md:grid-cols-3 gap-6">
                    <div className="md:col-span-2">
                        <UI.Card title="Active Subscriptions (Customer Base)">
                            <UI.Table 
                                columns={["id", "name", "email", "plan", "status"]} 
                                rows={users} 
                            />
                        </UI.Card>
                    </div>
                    <div>
                        <UI.Card title="MRR Monthly Growth Chart">
                            {growth.length > 0 ? (
                                <UI.Chart type="bar" data={growth} height={200} />
                            ) : (
                                <UI.Text>Loading chart metrics...</UI.Text>
                            )}
                        </UI.Card>
                    </div>
                </div>
            </div>
        </UI.Page>
}
"""
    },
    "ai-dashboard": {
        "description": "High-fidelity local AI assistant chatbot, chat threads, and inference metrics layout.",
        "app.pyreact": """# Premium AI Assistant Chatbot Dashboard Template
# Generated by PyReact Hub / Templates Marketplace (Q4 2028)

shared_state {
    "ai_assistant_model": "Llama-3 (Local)",
    "ai_messages_count": 0
}

server {
    def send_chat_prompt(prompt: str):
        # Integrates backend local Ollama fallback logic
        import urllib.request
        import json
        
        payload = {
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
        
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return {"status": "ok", "response": res_data.get("response", "")}
        except Exception:
            # Local Heuristical Rules Fallback if Ollama is Offline
            fallback_answers = {
                "hello": "Hello! I am your PyReact local AI assistant. How can I help you today?",
                "help": "You can ask me to help structure Python logic, design responsive JSX components, or build SQLite models.",
                "database": "PyReact supports built-in models! Simply define a model name and its database fields to connect instantly.",
                "about": "PyReact is a unified fullstack language transpileable directly into Flask, FastAPI, and React."
            }
            clean_prompt = prompt.lower().strip()
            ans = fallback_answers.get(clean_prompt, f"I received your prompt: '{prompt}'. [Local Fallback Mode: Offline Ollama]")
            return {"status": "ok", "response": ans}
}

component App() {
    state prompt = ""
    state response_text = "Ask me anything! Type a prompt in the input below to trigger local backend AI inference."
    state loading = False
    
    def process_ai_chat():
        if not prompt:
            return
        set_loading(True)
        res = server.send_chat_prompt(prompt)
        set_response_text(res["response"])
        set_prompt("")
        set_loading(False)
        setShared("ai_messages_count", shared.ai_messages_count + 1)
        
    render:
        <UI.Page>
            <UI.Navbar title="PyReact Local AI Console" />
            <div className="pt-24 max-w-4xl mx-auto px-4 pb-16">
                <div className="text-center mb-8">
                    <UI.Heading>AI Assistant Chat Arena</UI.Heading>
                    <UI.Text>Interact directly with local Ollama Llama-3 inference models running completely offline.</UI.Text>
                </div>
                
                <div className="grid md:grid-cols-4 gap-6">
                    <div className="md:col-span-3 space-y-6">
                        <UI.Card title="Inference Response Output Panel">
                            <div className="min-h-[160px] bg-white/5 rounded-xl border border-white/10 p-4 font-mono text-sm text-blue-300">
                                {loading ? "Generating response..." : response_text}
                            </div>
                        </UI.Card>
                        
                        <UI.Card title="Ask the Assistant">
                            <div className="flex gap-2 items-end">
                                <div className="flex-1">
                                    <UI.Input 
                                        label="Input Command / Prompt" 
                                        value={prompt} 
                                        onChange={set_prompt} 
                                        placeholder="e.g. hello, help, database..." 
                                    />
                                </div>
                                <UI.Button onClick={process_ai_chat} variant="primary" loading={loading} disabled={!prompt}>
                                    Send
                                </UI.Button>
                            </div>
                        </UI.Card>
                    </div>
                    
                    <div>
                        <UI.Card title="System Metrics">
                            <UI.Text size="sm">Active Model:</UI.Text>
                            <UI.Text size="xs" color="gray-400"><strong>{shared.ai_assistant_model}</strong></UI.Text>
                            <div className="mt-4">
                                <UI.Text size="sm">Messages Exchanged:</UI.Text>
                                <UI.Text size="lg" className="text-green-400 font-bold">{shared.ai_messages_count}</UI.Text>
                            </div>
                        </UI.Card>
                    </div>
                </div>
            </div>
        </UI.Page>
}
"""
    },
    "landing-page": {
        "description": "High-conversion product landing page layout, responsive sections, and pricing packages.",
        "app.pyreact": """# High-Conversion Product Landing Page Template
# Generated by PyReact Hub / Templates Marketplace (Q4 2028)

shared_state {
    "landing_email": "",
    "landing_subscribers": 1050
}

server {
    def subscribe_newsletter(email: str):
        if not email or "@" not in email:
            return {"status": "error", "message": "Please enter a valid email address."}
        return {"status": "ok", "message": "Thank you for subscribing! Welcome to PyReact Hub."}
}

component App() {
    state email = ""
    state success_msg = ""
    state error_msg = ""
    state loading = False
    
    def handle_subscribe():
        set_success_msg("")
        set_error_msg("")
        set_loading(True)
        res = server.subscribe_newsletter(email)
        if res["status"] == "ok":
            set_success_msg(res["message"])
            setShared("landing_subscribers", shared.landing_subscribers + 1)
            set_email("")
        else:
            set_error_msg(res["message"])
        set_loading(False)
        
    render:
        <UI.Page>
            <UI.Navbar title="Nusantara Digital Launch" />
            
            {/* Hero Section */}
            <div className="pt-32 pb-20 text-center max-w-4xl mx-auto px-4">
                <UI.Heading>Next-Gen Fullstack Application Builder</UI.Heading>
                <UI.Text className="mt-4 text-lg">
                    Build secure, ultra-fast Python backends paired with high-performance React frontends using one single unified file structure.
                </UI.Text>
                
                <div className="mt-10 flex justify-center gap-4">
                    <UI.Button variant="primary">Get Started Free</UI.Button>
                    <UI.Button variant="secondary">Read Documentation</UI.Button>
                </div>
            </div>
            
            {/* Features Grid */}
            <div className="py-16 max-w-6xl mx-auto px-4">
                <div className="grid md:grid-cols-3 gap-8">
                    <UI.Card title="Zero-Cost Local AI">
                        <UI.Text>Write commands in plain human language comment blocks and compile directly to live JSX elements.</UI.Text>
                    </UI.Card>
                    <UI.Card title="Multi-Platform Native">
                        <UI.Text>Compile to web dashboards, Tauri desktop apps, or Expo/React Native mobile applications instantly.</UI.Text>
                    </UI.Card>
                    <UI.Card title="WebSocket Sync">
                        <UI.Text>Keep client visual states fully synced with server databases in real-time without HTTP requests polling.</UI.Text>
                    </UI.Card>
                </div>
            </div>
            
            {/* Newsletter Subscription */}
            <div className="py-16 bg-white/5 border-t border-white/5">
                <div className="max-w-2xl mx-auto px-4 text-center">
                    <h3 className="text-xl font-bold text-white mb-2">Join the Community</h3>
                    <UI.Text className="mb-6">Stay up to date with core updates, templates releases, and package marketplace additions.</UI.Text>
                    
                    <div className="flex gap-2 items-end justify-center">
                        <div className="w-80">
                            <UI.Input 
                                label="Email Address" 
                                value={email} 
                                onChange={set_email} 
                                placeholder="Enter your email..." 
                            />
                        </div>
                        <UI.Button onClick={handle_subscribe} variant="primary" loading={loading}>
                            Subscribe
                        </UI.Button>
                    </div>
                    {success_msg && (
                        <div className="mt-4 text-green-400 text-sm font-semibold">{success_msg}</div>
                    )}
                    {error_msg && (
                        <div className="mt-4 text-red-400 text-sm font-semibold">{error_msg}</div>
                    )}
                    <UI.Text size="xs" color="gray-400" className="mt-4">
                        Current community size: <strong>{shared.landing_subscribers} developers</strong>
                    </UI.Text>
                </div>
            </div>
        </UI.Page>
}
"""
    }
}

def install_ppr_package(package_name: str, target_dir: Path) -> bool:
    """Download and unpack a PPR package to the project folder."""
    pkg = PPR_REGISTRY.get(package_name)
    if not pkg:
        print(f"  X  Package '{package_name}' not found in PyReact Package Registry.")
        return False
        
    print(f"  [PPR] Installing community package '{package_name}'...")
    print(f"  Description: {pkg['description']}")
    
    # Simulate download sequence
    for filename, content in pkg["files"].items():
        out_file = target_dir / filename
        out_file.write_text(content, encoding="utf-8")
        print(f"  [OK] Unpacked file -> {out_file.name}")
        
    print(f"  [OK] Successfully installed '{package_name}' into current project.\n")
    return True

def publish_ppr_package(file_path: Path) -> bool:
    """Simulate publishing a local .pyreact file to the PPR registry."""
    if not file_path.exists():
        print(f"  X  Target file '{file_path}' does not exist.")
        return False
        
    print(f"  [PPR] Analyzing and compiling '{file_path.name}' for PPR package publishing...")
    # Perform static analysis validation check
    content = file_path.read_text(encoding="utf-8")
    if "shared_state" not in content and "component" not in content:
        print("  X  Publish validation failed: Package must contain at least one visual component or shared state block.")
        return False
        
    print(f"  [PPR] Packaging code bundle (size: {len(content)} bytes)...")
    print(f"  [PPR] Uploading payload to PyReact Package Registry (PPR)...")
    print(f"  [OK] Successfully published package -> ppr://{file_path.stem.lower()}@0.1.0\n")
    return True

def list_registry_packages():
    """Display available PPR packages and descriptions."""
    print("  Available PPR Packages:")
    for name, info in PPR_REGISTRY.items():
        print(f"    *  {name:<15} - {info['description']}")
    print()

def list_marketplace_templates():
    """Display available Hub templates."""
    print("  Available Hub / Marketplace Templates:")
    for name, info in TEMPLATES.items():
        print(f"    *  {name:<15} - {info['description']}")
    print()

def init_hub_template(template_name: str, target_dir: Path) -> bool:
    """Initialize a project using a template from the Hub Marketplace."""
    tmpl = TEMPLATES.get(template_name)
    if not tmpl:
        print(f"  X  Template '{template_name}' not found in PyReact Hub Marketplace.")
        return False
        
    print(f"  [HUB] Initializing project using template '{template_name}'...")
    print(f"  Description: {tmpl['description']}")
    
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in tmpl.items():
        if filename == "description":
            continue
        out_file = target_dir / filename
        out_file.write_text(content, encoding="utf-8")
        print(f"  [OK] Created template asset -> {out_file.name}")
        
    # Write gitignore and default files
    gitignore = target_dir / ".gitignore"
    gitignore.write_text("dist/\n__pycache__/\nnode_modules/\n.env\n.pyreact-hmr-trigger\n")
    
    readme_content = f"""# PyReact Project: {template_name.upper()} 🚀

Proyek ini dibangun menggunakan **PyReact** — Bahasa pemrograman web fullstack bertenaga Python.

## 📦 Memulai Cepat

```bash
# 1. Jalankan server pengembangan (Flask + Vite)
pyreact dev
```

## 📂 Struktur Proyek

* `app.pyreact` — File entry point utama aplikasi Anda.
* `AGENTS.md` — Panduan sintaksis PyReact khusus untuk asisten AI (seperti Cursor/Claude/Copilot).
* `COOKBOOK.md` — Resep-resep pengerjaan umum (CRUD, Auth, Chart, dll.) siap pakai.
* `.cursorrules` — File rules untuk Cursor IDE.
* `components/` — Folder untuk meletakkan komponen tambahan.
"""
    readme = target_dir / "README.md"
    readme.write_text(readme_content, encoding="utf-8")
    
    # Generate local AI context files using cli helpers
    try:
        from pyreact.cli import _generate_agents_md, _generate_cookbook_md, _generate_cursorrules, _create_components_dir
        (target_dir / "AGENTS.md").write_text(_generate_agents_md(), encoding="utf-8")
        (target_dir / "COOKBOOK.md").write_text(_generate_cookbook_md(), encoding="utf-8")
        (target_dir / ".cursorrules").write_text(_generate_cursorrules(), encoding="utf-8")
        _create_components_dir(target_dir)
        print("  [OK] Created local AI context files (AGENTS.md, COOKBOOK.md, .cursorrules)")
    except ImportError:
        pass
        
    print(f"  [OK] Successfully initialized marketplace template in '{target_dir}' directory.\n")
    return True
