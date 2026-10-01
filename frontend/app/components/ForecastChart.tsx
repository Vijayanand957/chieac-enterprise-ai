"use client";

import { useEffect, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { getForecast, ForecastPoint } from "../../lib/api";

export default function ForecastChart({ target = "churn" }: { target?: string }) {
  const [data, setData] = useState<ForecastPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getForecast(target, 30)
      .then((res) => setData(res.forecast))
      .catch(() => setError("Could not load forecast. Ensure enough historical data is loaded."));
  }, [target]);

  if (error) return <div className="text-sm text-red-500">{error}</div>;

  return (
    <div className="w-full h-80">
      <h3 className="font-semibold mb-2">30-day forecast: {target}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis />
          <Tooltip />
          <Area dataKey="upper" stroke="none" fill="#93c5fd" fillOpacity={0.3} />
          <Area dataKey="lower" stroke="none" fill="#ffffff" fillOpacity={1} />
          <Line dataKey="predicted" stroke="#2563eb" strokeWidth={2} dot={false} />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
