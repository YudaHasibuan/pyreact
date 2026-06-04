import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const Home = React.lazy(() => import("./Home"));
const About = React.lazy(() => import("./About"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Settings = React.lazy(() => import("./Settings"));
const Login = React.lazy(() => import("./Login"));

export default function Blog({}) {
  const [shared, setShared] = useSharedState();
  const [posts, setPosts] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  const fetchPosts = async () => {
  setLoading(true);
  const data = await server.get_posts({});
  setPosts(data);
  setLoading(false);
  };

  return (
    <UI.Page>
                <UI.Navbar title="Blog PyReact" />
                <div className="pt-24 max-w-4xl mx-auto px-6">
                    <div className="flex items-center justify-between mb-6">
                        <UI.Heading>Blog</UI.Heading>
                        <UI.Button onClick={fetchPosts}>Refresh</UI.Button>
                    </div>
                    {loading && <UI.Spinner />}
                    {posts && (
                        <div className="grid gap-4">
                            {posts.map(p => (
                                <UI.Card key={p.id} title={p.title}>
                                    <UI.Badge color="blue">{p.author}</UI.Badge>
                                </UI.Card>
                            ))}
                        </div>
                    )}
                    {!posts && !loading && (
                        <UI.Alert type="info">Klik Refresh untuk memuat artikel.</UI.Alert>
                    )}
                </div>
            </UI.Page>
  );
}
