import React, { useState } from 'react';
import { SafeAreaView, ScrollView, View, Text, TouchableOpacity, TextInput, StyleSheet } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export function Home({  }) {
  const [posts, setPosts] = useState(null);
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <View style={styles.navbar}><Text style={styles.navbarTitle}>PyReact App</Text></View>
            <div className="pt-24 max-w-5xl mx-auto px-6">
                <Text style={styles.heading}>Selamat Datang di PyReact</Text>
                <UI.Text className="mt-2 text-gray-400">
                    Framework fullstack Python + React dalam satu file.
                </Text>

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
                    <UI.Button onClick={loadPosts}>Muat Posts</Text></TouchableOpacity>
                    {posts && (
                        <div className="mt-4 grid gap-4">
                            {posts.map(p => (
                                <UI.Card key={p.id} title={p.title}>
                                    <Text style={styles.text}>Oleh: {p.author}</Text>
                                </View>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </ScrollView></SafeAreaView>
  );
}

export function About({  }) {
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <View style={styles.navbar}><Text style={styles.navbarTitle}>Tentang PyReact</Text></View>
            <div className="pt-24 max-w-3xl mx-auto px-6">
                <Text style={styles.heading}>Tentang PyReact</Text>
                <UI.Text className="mt-4 text-gray-300 leading-relaxed">
                    PyReact adalah bahasa pemrograman fullstack inovatif yang memungkinkan
                    developer membangun aplikasi web lengkap dalam satu file .pyreact.
                </Text>
                <div className="mt-6 grid md:grid-cols-3 gap-4">
                    <View style={styles.card}><Text style={styles.cardTitle}>Flask Backend</Text>
                        <Text style={styles.text}>Auto-generate Python Flask API dengan routing lengkap.</Text>
                    </View>
                    <View style={styles.card}><Text style={styles.cardTitle}>React Frontend</Text>
                        <Text style={styles.text}>Kompilasi JSX + Tailwind CSS secara otomatis.</Text>
                    </View>
                    <View style={styles.card}><Text style={styles.cardTitle}>Self-Healing</Text>
                        <Text style={styles.text}>AI auto-fix syntax error via Ollama lokal.</Text>
                    </View>
                </div>
            </div>
        </ScrollView></SafeAreaView>
  );
}

export function Blog({  }) {
  const [posts, setPosts] = useState(null);
  const [loading, setLoading] = useState(false);
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <View style={styles.navbar}><Text style={styles.navbarTitle}>Blog PyReact</Text></View>
            <div className="pt-24 max-w-4xl mx-auto px-6">
                <div className="flex items-center justify-between mb-6">
                    <Text style={styles.heading}>Blog</Text>
                    <UI.Button onClick={fetchPosts}>Refresh</Text></TouchableOpacity>
                </div>
                {loading && <UI.Spinner />}
                {posts && (
                    <div className="grid gap-4">
                        {posts.map(p => (
                            <UI.Card key={p.id} title={p.title}>
                                <UI.Badge color="blue">{p.author}</UI.Badge>
                            </View>
                        ))}
                    </div>
                )}
                {!posts && !loading && (
                    <UI.Alert type="info">Klik Refresh untuk memuat artikel.</UI.Alert>
                )}
            </div>
        </ScrollView></SafeAreaView>
  );
}

export function Dashboard({  }) {
  const [user, setUser] = useState(null);
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <View style={styles.navbar}><Text style={styles.navbarTitle}>Dashboard</Text></View>
            <div className="pt-24 max-w-5xl mx-auto px-6">
                <Text style={styles.heading}>Dashboard</Text>
                <UI.Alert type="warning" className="mt-4">
                    Halaman ini membutuhkan autentikasi. (Protected Route)
                </UI.Alert>
                <div className="mt-6">
                    <UI.Button onClick={loadMe}>Muat User</Text></TouchableOpacity>
                    {user && (
                        <View style={styles.card}><Text style={styles.cardTitle}>User Info" className="mt-4</Text>
                            <Text style={styles.text}>Nama: {user.name}</Text>
                            <UI.Badge color="green">{user.role}</UI.Badge>
                        </View>
                    )}
                </div>
            </div>
        </ScrollView></SafeAreaView>
  );
}

export function Settings({  }) {
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <View style={styles.navbar}><Text style={styles.navbarTitle}>Settings</Text></View>
            <div className="pt-24 max-w-3xl mx-auto px-6">
                <Text style={styles.heading}>Pengaturan</Text>
                <View style={styles.card}><Text style={styles.cardTitle}>Preferensi" className="mt-6</Text>
                    <Text style={styles.text}>Pengaturan akun dan preferensi aplikasi.</Text>
                </View>
            </div>
        </ScrollView></SafeAreaView>
  );
}

export function Login({  }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  return (
    <SafeAreaView style={styles.page}><ScrollView contentContainerStyle={styles.scroll}>
            <div className="min-h-screen flex items-center justify-center p-4">
                <View style={styles.card}><Text style={styles.cardTitle}>Login ke PyReact" className="w-full max-w-sm</Text>
                    <div className="flex flex-col gap-4">
                        <UI.Input label="Username" value={username} onChange={setUsername} placeholder="admin" />
                        <View style={styles.inputContainer}><Text style={styles.inputLabel}>Password" value={password} onChange={setPassword} type="password</Text><TextInput placeholder="••••••" placeholderTextColor="#666" style={styles.input} /></View>
                        {error && <UI.Alert type="error">{error}</UI.Alert>}
                        <UI.Button onClick={handleLogin}>Masuk</Text></TouchableOpacity>
                    </div>
                </View>
            </div>
        </ScrollView></SafeAreaView>
  );
}

export default function App() {
  return <Home />;
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: '#090d16',
  },
  scroll: {
    padding: 16,
  },
  navbar: {
    height: 60,
    backgroundColor: '#111827',
    borderBottomWidth: 1,
    borderBottomColor: '#ffffff1a',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    borderRadius: 8,
  },
  navbarTitle: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  card: {
    backgroundColor: '#111827',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#ffffff1a',
    padding: 16,
    marginBottom: 16,
  },
  cardTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  heading: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 12,
  },
  text: {
    fontSize: 14,
    color: '#9ca3af',
    lineHeight: 20,
    marginBottom: 8,
  },
  button: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    marginBottom: 8,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  inputContainer: {
    marginBottom: 16,
  },
  inputLabel: {
    color: '#9ca3af',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
  },
  input: {
    backgroundColor: '#1f2937',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#374151',
    padding: 10,
    color: '#ffffff',
    fontSize: 14,
  },
});
