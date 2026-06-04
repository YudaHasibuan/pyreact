import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const Home = React.lazy(() => import("./Home"));
const About = React.lazy(() => import("./About"));
const Blog = React.lazy(() => import("./Blog"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Settings = React.lazy(() => import("./Settings"));

export default function Login({}) {
  const [shared, setShared] = useSharedState();
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState(null);

  const handleLogin = async () => {
// Transpilation error: sequence item 0: expected str instance, NoneType found
// if username and password:
//     import localStorage
//     localStorage.setItem("pyreact_token", "demo_token_123")
//     window.location.pathname = "/dashboard"
// else:
//     setError("Username dan password tidak boleh kosong.")
  };

  return (
    <UI.Page>
                <div className="min-h-screen flex items-center justify-center p-4">
                    <UI.Card title="Login ke PyReact" className="w-full max-w-sm">
                        <div className="flex flex-col gap-4">
                            <UI.Input label="Username" value={username} onChange={setUsername} placeholder="admin" />
                            <UI.Input label="Password" value={password} onChange={setPassword} type="password" placeholder="••••••" />
                            {error && <UI.Alert type="error">{error}</UI.Alert>}
                            <UI.Button onClick={handleLogin}>Masuk</UI.Button>
                        </div>
                    </UI.Card>
                </div>
            </UI.Page>
  );
}
