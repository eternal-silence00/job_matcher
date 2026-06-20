import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { tokens } from "../api.js";
import { cleanDescription } from "../lib/text.js";

export default function Dashboard() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [resume, setResume] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [error, setError] = useState("");
  const [hours, setHours] = useState("");

  const loadResume = async () => {
    try {
      const { data } = await api.get("/resumes/me");
      setResume(data);
    } catch {
      setResume(null);
    }
  };

  const loadJobs = async () => {
    setLoadingJobs(true);
    setError("");
    try {
      const params = hours ? { hours: Number(hours) } : {};
      const { data } = await api.get("/matching/jobs", { params });
      setJobs(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Не удалось загрузить вакансии");
    } finally {
      setLoadingJobs(false);
    }
  };

  useEffect(() => {
    loadResume();
  }, []);

  // перезагружаем вакансии при первом рендере и при смене фильтра
  useEffect(() => {
    loadJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [hours]);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const { data } = await api.post("/resumes", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResume(data);
      setFile(null);
      await loadJobs();
    } catch (err) {
      setError(err.response?.data?.detail || "Ошибка загрузки резюме");
    } finally {
      setUploading(false);
    }
  };

  const handleLogout = async () => {
    try {
      if (tokens.refresh) {
        await api.post("/auth/logout", { refresh_token: tokens.refresh });
      }
    } catch {
      // даже если запрос упал — всё равно чистим клиент и выходим
    } finally {
      tokens.clear();
      navigate("/login");
    }
  };

  const formatSalary = (from, to) => {
    if (!from && !to) return null;
    if (from && to) return `${from.toLocaleString()} – ${to.toLocaleString()}`;
    return `от ${(from || to).toLocaleString()}`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">AI Job Matcher</h1>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-600 hover:text-indigo-600"
          >
            Выйти
          </button>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8 space-y-8">
        <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Резюме</h2>
          {resume && (
            <div className="mb-4 p-3 bg-indigo-50 border border-indigo-100 rounded-lg text-sm">
              <span className="text-gray-700">Текущее резюме: </span>
              <a
                href={resume.file_url}
                target="_blank"
                rel="noreferrer"
                className="text-indigo-600 font-medium hover:underline"
              >
                {resume.filename}
              </a>
            </div>
          )}
          <form onSubmit={handleUpload} className="flex flex-col sm:flex-row gap-3">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="flex-1 text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
            />
            <button
              type="submit"
              disabled={!file || uploading}
              className="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
            >
              {uploading ? "Загрузка..." : "Загрузить PDF"}
            </button>
          </form>
        </section>

        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              Подходящие вакансии
            </h2>
            <div className="flex items-center gap-3">
              <select
                value={hours}
                onChange={(e) => setHours(e.target.value)}
                className="text-sm border border-gray-300 rounded-lg px-2 py-1.5 text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">За всё время</option>
                <option value="24">За 24 часа</option>
                <option value="72">За 3 дня</option>
                <option value="168">За неделю</option>
              </select>
              <button
                onClick={loadJobs}
                className="text-sm text-indigo-600 hover:text-indigo-800"
              >
                Обновить
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          {loadingJobs ? (
            <div className="text-gray-500 text-sm">Загрузка...</div>
          ) : jobs.length === 0 ? (
            <div className="bg-white border border-dashed border-gray-300 rounded-2xl p-8 text-center text-gray-500">
              {resume
                ? "Нет подходящих вакансий за выбранный период"
                : "Загрузите резюме, чтобы увидеть подходящие вакансии"}
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => {
                const salary = formatSalary(job.salary_from, job.salary_to);
                return (
                  <article
                    key={job.id}
                    className="bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-md transition"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="font-semibold text-gray-900">
                          {job.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-0.5">
                          {job.company} · {job.location}
                        </p>
                      </div>
                      {salary && (
                        <span className="text-sm font-medium text-indigo-600 whitespace-nowrap">
                          {salary}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-3 line-clamp-3">
                      {cleanDescription(job.description)}
                    </p>
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-block mt-3 text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      Открыть вакансию →
                    </a>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
