import ChatWindow from "./components/ChatWindow";
import ForecastChart from "./components/ForecastChart";

export default function Home() {
  return (
    <main className="min-h-screen grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 bg-gray-50">
      <section className="bg-white rounded-xl shadow p-4 h-[80vh]">
        <h2 className="text-lg font-bold mb-2">AI Operations Assistant</h2>
        <ChatWindow />
      </section>
      <section className="bg-white rounded-xl shadow p-6 space-y-6">
        <h2 className="text-lg font-bold">Predictive Insights</h2>
        <ForecastChart target="incidents" />
        <ForecastChart target="churn" />
      </section>
    </main>
  );
}
