import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const Home = React.lazy(() => import("./Home"));
const Blog = React.lazy(() => import("./Blog"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Settings = React.lazy(() => import("./Settings"));
const Login = React.lazy(() => import("./Login"));

export default function About({}) {
  const [shared, setShared] = useSharedState();

  return (
    <UI.Page>
                <UI.Navbar title="Tentang PyReact" />
                <div className="pt-24 max-w-3xl mx-auto px-6">
                    <UI.Heading>Tentang PyReact</UI.Heading>
                    <UI.Text className="mt-4 text-gray-300 leading-relaxed">
                        PyReact adalah bahasa pemrograman fullstack inovatif yang memungkinkan
                        developer membangun aplikasi web lengkap dalam satu file .pyreact.
                    </UI.Text>
                    <div className="mt-6 grid md:grid-cols-3 gap-4">
                        <UI.Card title="Flask Backend">
                            <UI.Text>Auto-generate Python Flask API dengan routing lengkap.</UI.Text>
                        </UI.Card>
                        <UI.Card title="React Frontend">
                            <UI.Text>Kompilasi JSX + Tailwind CSS secara otomatis.</UI.Text>
                        </UI.Card>
                        <UI.Card title="Self-Healing">
                            <UI.Text>AI auto-fix syntax error via Ollama lokal.</UI.Text>
                        </UI.Card>
                    </div>
                </div>
            </UI.Page>
  );
}
