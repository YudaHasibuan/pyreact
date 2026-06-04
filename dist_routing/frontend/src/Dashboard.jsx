import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const Home = React.lazy(() => import("./Home"));
const About = React.lazy(() => import("./About"));
const Blog = React.lazy(() => import("./Blog"));
const Settings = React.lazy(() => import("./Settings"));
const Login = React.lazy(() => import("./Login"));

export default function Dashboard({}) {
  const [shared, setShared] = useSharedState();
  const [user, setUser] = React.useState(null);

  const loadMe = async () => {
  const data = await server.get_user({'1'});
  setUser(data);
  };

  return (
    <UI.Page>
                <UI.Navbar title="Dashboard" />
                <div className="pt-24 max-w-5xl mx-auto px-6">
                    <UI.Heading>Dashboard</UI.Heading>
                    <UI.Alert type="warning" className="mt-4">
                        Halaman ini membutuhkan autentikasi. (Protected Route)
                    </UI.Alert>
                    <div className="mt-6">
                        <UI.Button onClick={loadMe}>Muat User</UI.Button>
                        {user && (
                            <UI.Card title="User Info" className="mt-4">
                                <UI.Text>Nama: {user.name}</UI.Text>
                                <UI.Badge color="green">{user.role}</UI.Badge>
                            </UI.Card>
                        )}
                    </div>
                </div>
            </UI.Page>
  );
}
