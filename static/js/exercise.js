/*
  Exercise page logic extracted from templates/exercise.html
  - Defines workoutPlans
  - Exposes functions used by inline buttons: loadWorkoutPlan, fillExerciseTemplate, fillExerciseTemplateFromPlan, copyPreviousExercise
  - Initializes sliders, default datetime, and renders charts from JSON provided by #trend-data
*/
(function () {
  'use strict';

  // Workout plans database
  const workoutPlans = {
    workout_a: {
      name: 'Workout A - Full Body (Horizontal Focus)',
      exercises: [
        { name: 'Barbell Back Squat', type: 'strength', sets: 4, reps: '6-10', category: 'Lower Body (Squat Pattern)' },
        { name: 'Bench Press (Barbell)', type: 'strength', sets: 4, reps: '6-10', category: 'Upper Body (Horizontal Push)' },
        { name: 'Dumbbell Rows', type: 'strength', sets: 4, reps: '8-12 per arm', category: 'Upper Body (Horizontal Pull)' },
        { name: 'Dumbbell Lateral Raises', type: 'strength', sets: 3, reps: '10-15', category: 'Shoulders (Lateral Head)' },
        { name: 'Plank', type: 'strength', sets: 3, reps: 'Hold for Time', category: 'Core (Anterior Stability)' }
      ]
    },
    workout_b: {
      name: 'Workout B - Full Body (Posterior Chain Focus)',
      exercises: [
        { name: '45-Degree Back Extension', type: 'strength', sets: 4, reps: '10-15', category: 'Posterior Chain (Hinge Pattern)' },
        { name: 'Seated Dumbbell Shoulder Press', type: 'strength', sets: 4, reps: '8-12', category: 'Upper Body (Vertical Push)' },
        { name: 'Lat Pulldowns', type: 'strength', sets: 4, reps: '8-12', category: 'Upper Body (Vertical Pull)' },
        { name: 'Seated Cable Rows', type: 'strength', sets: 3, reps: '10-15', category: 'Upper Back / Posture' },
        { name: 'Leg Press', type: 'strength', sets: 3, reps: '10-15', category: 'Lower Body (Accessory)' }
      ]
    }
  };

  function loadWorkoutPlan(planName) {
    const plan = workoutPlans[planName];
    if (!plan) return;

    // Show workout plan notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-blue-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 max-w-md';
    notification.innerHTML = `
      <div class="font-semibold mb-1">${plan.name}</div>
      <div class="text-sm">Ready to log! Click exercises below to fill the form.</div>
    `;
    document.body.appendChild(notification);

    // Create workout plan interface
    createWorkoutPlanInterface(plan);

    // Remove notification after 4 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        if (notification.parentElement) notification.parentElement.removeChild(notification);
      }, 300);
    }, 4000);
  }

  function createWorkoutPlanInterface(plan) {
    // Remove existing workout plan interface if any
    const existing = document.getElementById('workout-plan-interface');
    if (existing) existing.remove();

    // Create new interface
    const interfaceDiv = document.createElement('div');
    interfaceDiv.id = 'workout-plan-interface';
    interfaceDiv.className = 'mt-4 p-4 bg-blue-50 rounded-lg border-2 border-blue-200';

    interfaceDiv.innerHTML = `
      <div class="flex items-center justify-between mb-3">
        <h5 class="font-semibold text-blue-900">${plan.name}</h5>
        <button class="close-plan text-blue-600 hover:text-blue-800" aria-label="Close workout plan">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      <div class="space-y-2">
        ${plan.exercises.map(exercise => `
          <button class="plan-ex-btn w-full text-left p-2 bg-white rounded hover:bg-blue-100 transition-colors flex justify-between items-center"
                  data-name="${exercise.name}"
                  data-type="${exercise.type}"
                  data-sets="${exercise.sets}"
                  data-reps="${exercise.reps}">
            <span class="font-medium">${exercise.name}</span>
            <span class="text-sm text-gray-600">${exercise.sets}x${exercise.reps}</span>
          </button>
        `).join('')}
      </div>
    `;

    // Insert after the workout plan selector container
    const selectorGrid = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.gap-4');
    const container = selectorGrid ? selectorGrid.parentElement : null;
    if (container) {
      container.appendChild(interfaceDiv);
      // Close button
      const closeBtn = interfaceDiv.querySelector('.close-plan');
      if (closeBtn) closeBtn.addEventListener('click', () => interfaceDiv.remove());
      // Attach listeners to plan exercise buttons
      interfaceDiv.querySelectorAll('.plan-ex-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const name = btn.dataset.name;
          const type = btn.dataset.type;
          const sets = parseInt(btn.dataset.sets || '0', 10);
          const reps = btn.dataset.reps || '';
          fillExerciseTemplateFromPlan(name, type, sets, reps);
        });
      });
    }
  }

  function fillExerciseTemplate(exerciseName, exerciseType, sets, reps, weight) {
    const nameEl = document.getElementById('exercise-name');
    const typeEl = document.getElementById('exercise-type');
    const setsEl = document.getElementById('sets');
    const repsEl = document.getElementById('reps');
    const weightEl = document.getElementById('weight');
    if (nameEl) nameEl.value = exerciseName;
    if (typeEl) typeEl.value = exerciseType;
    if (setsEl) setsEl.value = sets;
    if (repsEl) repsEl.value = reps;
    if (weightEl) weightEl.value = weight || '';
    if (nameEl) {
      nameEl.focus();
      nameEl.scrollIntoView({ behavior: 'smooth' });
    }
  }

  function fillExerciseTemplateFromPlan(exerciseName, exerciseType, sets, reps) {
    const parsedReps = parseRepsInput(reps);
    fillExerciseTemplate(exerciseName, exerciseType, sets, parsedReps, '');
    notify(`Exercise "${exerciseName}" loaded from workout plan! Adjust weight as needed.`);
  }

  function copyPreviousExercise(exerciseName, exerciseType, sets, reps, weight) {
    fillExerciseTemplate(exerciseName, exerciseType, sets, reps, weight);
    notify('Previous exercise copied! You can modify the values before submitting.');
  }

  function notify(message) {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => {
        if (notification.parentElement) notification.parentElement.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // Parse reps input that might be a range or text (e.g., "6-10", "8-12 per arm", "Hold for Time")
  // Returns a sensible numeric default or empty string if no number found.
  function parseRepsInput(repsRaw) {
    if (typeof repsRaw === 'number' && Number.isFinite(repsRaw)) return repsRaw;
    if (!repsRaw || typeof repsRaw !== 'string') return '';
    const nums = (repsRaw.match(/\d+/g) || []).map(n => parseInt(n, 10)).filter(n => !Number.isNaN(n));
    if (nums.length === 0) return '';
    if (nums.length === 1) return nums[0];
    // If a range like 6-10, average it; if multiple numbers (per arm), average them
    const avg = Math.round(nums.reduce((a, b) => a + b, 0) / nums.length);
    return avg;
  }

  function parseTrendData() {
    try {
      const tEl = document.getElementById('trend-data');
      if (!tEl) return { labels: [], form: [], effort: [], quality: [], volume: [] };
      return JSON.parse(tEl.textContent || '{}');
    } catch (e) {
      console.warn('Failed to parse trend data JSON', e);
      return { labels: [], form: [], effort: [], quality: [], volume: [] };
    }
  }

  function initCharts() {
    if (typeof Chart === 'undefined') return;
    const { labels, form, effort, quality, volume } = parseTrendData();

    const qEl = document.getElementById('qualityChart');
    if (qEl) {
      // Make canvas responsive height
      if (qEl.parentElement) qEl.parentElement.style.minHeight = '240px';
      new Chart(qEl, {
        type: 'line',
        data: {
          labels,
          datasets: [
            { label: 'Form (avg)', data: form, borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', tension: 0.3, spanGaps: true },
            { label: 'Effort (avg)', data: effort, borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,0.1)', tension: 0.3, spanGaps: true },
            { label: 'Quality (avg)', data: quality, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.3, spanGaps: true }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
      });
    }

    const vEl = document.getElementById('volumeChart');
    if (vEl) {
      if (vEl.parentElement) vEl.parentElement.style.minHeight = '240px';
      new Chart(vEl, {
        type: 'bar',
        data: {
          labels,
          datasets: [{ label: 'Volume (lbs)', data: volume, backgroundColor: 'rgba(156,163,175,0.6)', borderColor: '#374151' }]
        },
        options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true } } }
      });
    }
  }

  function initFormDefaults() {
    // Default workout time to now (local)
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    const timeEl = document.getElementById('workout-time');
    if (timeEl) timeEl.value = localDateTime;

    // Range slider labels
    const formEl = document.getElementById('form-score');
    const effortEl = document.getElementById('effort-score');
    if (formEl) {
      formEl.value = 3;
      const formVal = document.getElementById('form-score-value');
      if (formVal) formVal.innerText = formEl.value;
      formEl.addEventListener('input', () => {
        const v = document.getElementById('form-score-value');
        if (v) v.innerText = formEl.value;
      });
    }
    if (effortEl) {
      effortEl.value = 7;
      const effortVal = document.getElementById('effort-score-value');
      if (effortVal) effortVal.innerText = effortEl.value;
      effortEl.addEventListener('input', () => {
        const v = document.getElementById('effort-score-value');
        if (v) v.innerText = effortEl.value;
      });
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    initFormDefaults();
    initCharts();
    // Attach plan loader buttons
    document.querySelectorAll('.load-plan-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const plan = btn.dataset.plan;
        if (plan) loadWorkoutPlan(plan);
      });
    });
    // Attach quick template buttons
    document.querySelectorAll('.quick-template-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const name = btn.dataset.name;
        const type = btn.dataset.type;
        const sets = parseInt(btn.dataset.sets || '0', 10);
        const reps = parseInt(btn.dataset.reps || '0', 10);
        const weight = btn.dataset.weight !== undefined ? parseFloat(btn.dataset.weight) : '';
        fillExerciseTemplate(name, type, sets, reps, weight);
      });
    });
    // Attach copy previous buttons
    document.querySelectorAll('.copy-previous-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const name = btn.dataset.name;
        const type = btn.dataset.type;
        const sets = parseInt(btn.dataset.sets || '0', 10);
        const reps = parseInt(btn.dataset.reps || '0', 10);
        const weight = btn.dataset.weight !== undefined ? parseFloat(btn.dataset.weight) : '';
        copyPreviousExercise(name, type, sets, reps, weight);
      });
    });
  });

  // Expose functions for inline onclick handlers used by the template
  window.loadWorkoutPlan = loadWorkoutPlan;
  window.fillExerciseTemplate = fillExerciseTemplate;
  window.fillExerciseTemplateFromPlan = fillExerciseTemplateFromPlan;
  window.copyPreviousExercise = copyPreviousExercise;
})();
