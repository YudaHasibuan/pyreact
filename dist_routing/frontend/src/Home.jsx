import React from "react";
import { UI } from "./ui/components";
import { server } from "./pybridge";
import { useSharedState } from "./store";
const About = React.lazy(() => import("./About"));
const Blog = React.lazy(() => import("./Blog"));
const Dashboard = React.lazy(() => import("./Dashboard"));
const Settings = React.lazy(() => import("./Settings"));
const Login = React.lazy(() => import("./Login"));

export default function Home({}) {
  const [shared, setShared] = useSharedState();
  const [posts, setPosts] = React.useState(null);

  const loadPosts = async () => {
  const data = await server.get_posts({});
  setPosts(data);
  };

  return (
    <UI.Page>
                <UI.Navbar title="PyReact App" />
                <div className="pt-24 max-w-5xl mx-auto px-6">
                    <UI.Heading>Selamat Datang di PyReact</UI.Heading>
                    <UI.Text className="mt-2 text-gray-400">
                        Framework fullstack Python + React dalam satu file.
                    </UI.Text>
    
                    <div className="mt-6 flex gap-3 flex-wrap">
                        <a href="/blog"
                           onClick="(e) => { e.preventDefault(); window.history.pushState(null,'','/blog'); window.dispatchEvent(new PopStateEvent('popstate')); }"
                           className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold transition">
                            Lihat Blog
                        </a>
                        <a href="/dashboard"
                           className="px-5 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-sm font-semibold transition border border-white/10">
                            Dashboard (Protected)
                        </a>
                    </div>
    
                    <div className="mt-10">
                        <UI.Button onClick={loadPosts}>Muat Posts</UI.Button>
                        {posts && (
                            <div className="mt-4 grid gap-4">
                                {posts.map(p => (
                                    <UI.Card key={p.id} title={p.title}>
                                        <UI.Text>Oleh: {p.author}</UI.Text>
                                    </UI.Card>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </UI.Page>
  );
}
