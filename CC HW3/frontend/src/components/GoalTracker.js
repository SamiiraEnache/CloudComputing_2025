import React, { useEffect, useState } from "react";
import "./GoalTracker.css";

export default function GoalTracker() {
  const [goals, setGoals] = useState([]);
  const [newGoal, setNewGoal] = useState("");
  const [image, setImage] = useState(null);
  const [taskId, setTaskId] = useState(null);

  useEffect(() => {
    const loadGoals = async () => {
      try {
        const res = await fetch("/api/goals");
        const data = await res.json();

        const transformed = data.map((goal) => ({
          id: goal.id,
          text: goal.task,
          completed: goal.completed,
          imageUrl: goal.image_url || "",
        }));

        setGoals(transformed);
      } catch (err) {
        console.error("Eroare la încărcare goals:", err);
      }
    };

    loadGoals();
  }, []);

  const toggleGoal = async (id) => {
    const updated = goals.map((g) =>
      g.id === id ? { ...g, completed: !g.completed } : g
    );
    setGoals(updated);

    const goal = updated.find((g) => g.id === id);
    await fetch(`/api/goals/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ completed: goal.completed }),
    });
  };

  const handleAddGoal = async () => {
    if (!newGoal.trim()) return;

    const res = await fetch("/api/goals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task: newGoal,
        deadline: null,
      }),
    });

    const data = await res.json();
    setGoals([...goals, { id: data.id, text: data.task, completed: false }]);
    setNewGoal("");
  };

  const handleFileChange = async (e, taskId) => {
    const selectedImage = e.target.files[0];
    setImage(selectedImage);
    setTaskId(taskId);
    console.log("File selected:", selectedImage);

    if (selectedImage && taskId !== null) {
      const formData = new FormData();
      formData.append("image", selectedImage);
      formData.append("task_id", taskId);

      const res = await fetch("/api/upload-photo", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("Uploaded image URL:", data.image_url);

      const updatedGoals = goals.map((goal) =>
        goal.id === taskId ? { ...goal, imageUrl: data.image_url } : goal
      );
      setGoals(updatedGoals);
    }
  };

  return (
    <div className="goal-wrapper">
      <div className="goal-container">
        <h1>🌟 Daily Goal Tracker</h1>

        <div className="goal-add">
          <input
            type="text"
            placeholder="Introduceți un nou goal"
            value={newGoal}
            onChange={(e) => setNewGoal(e.target.value)}
          />
          <button onClick={handleAddGoal}>Adaugă</button>
        </div>

        <div className="goal-list">
          {goals.map((goal) => (
            <div
              key={goal.id}
              className={`goal-card ${goal.completed ? "completed" : ""}`}
            >
              <input
                type="checkbox"
                checked={goal.completed}
                onChange={() => toggleGoal(goal.id)}
              />
              <span>{goal.text}</span>

              <div className="upload-button">
                <label className="upload-label" htmlFor={`upload-${goal.id}`}>
                  Încarcă dovada vizuală
                </label>
                <input
                  type="file"
                  id={`upload-${goal.id}`}
                  accept="image/*"
                  onChange={(e) => handleFileChange(e, goal.id)}
                  style={{ display: "none" }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="incarcari-container">
        <h2>Uploads</h2>
        <div className="incarcari-list">
          {goals
            .filter((goal) => goal.imageUrl)
            .map((goal) => (
              <div key={goal.id} className="image-item">
                <img src={goal.imageUrl} alt="Dovada goal-ului" />
                <span className="image-description">{goal.text}</span>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}