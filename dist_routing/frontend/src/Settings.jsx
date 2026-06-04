import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const Home = React.lazy(() => import("./Home"));
const About = React.lazy(() => import("./About"));
const Blog = React.lazy(() => import("./Blog"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Login = React.lazy(() => import("./Login"));

export default function Settings({}) {
  const [shared, setShared] = useSharedState();

  return (
    <UI.Page>
                <UI.Navbar title="Settings" />
                <div className="pt-24 max-w-3xl mx-auto px-6">
                    <UI.Heading>Pengaturan</UI.Heading>
                    <UI.Card title="Preferensi" className="mt-6">
                        <UI.Text>Pengaturan akun dan preferensi aplikasi.</UI.Text>
                    </UI.Card>
                </div>
            </UI.Page>
  );
}
