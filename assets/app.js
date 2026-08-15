const categories = ["All", "AI", "Dev", "Hardware", "Security", "Startups"];
let activeCategory = "All";
let stories = [];
let activeMode = "daily";

const prettyDate = (value) => new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));

function renderCategories() {
  document.querySelector("#categories").innerHTML = categories.map((category) =>
    `<button class="category ${category === activeCategory ? "active" : ""}" data-category="${category}">${category}</button>`
  ).join("");
  document.querySelectorAll("[data-category]").forEach((button) => button.addEventListener("click", () => {
    activeCategory = button.dataset.category;
    renderCategories();
    renderStories();
  }));
}

function renderStories() {
  const visible = activeCategory === "All" ? stories : stories.filter((story) => story.category === activeCategory);
  document.querySelector("#story-count").textContent = `${visible.length} stories`;
  document.querySelector("#news-list").innerHTML = visible.map((story, index) => `
    <article class="story">
      <span class="story-number">${index + 1}</span>
      <div><h3><a href="${story.url}" target="_blank" rel="noreferrer">${story.title}</a></h3>
      <p>${story.description}</p><span class="story-meta">${story.category} · ${story.source}</span>
      <p class="work-signal">${story.workSignal || "Worth a quick look for a practical takeaway."}</p></div>
    </article>`).join("") || "<p>No stories in this category today.</p>";
}

function renderBrief(brief) {
  stories = brief.stories;
  document.querySelector("#brief-date").textContent = prettyDate(brief.generatedAt);
  document.querySelector("#top-story-label").textContent = activeMode === "weekly" ? "Stack signal" : "Top story";
  document.querySelector("#top-title").textContent = brief.topStory.title;
  document.querySelector("#top-description").textContent = brief.topStory.description;
  document.querySelector("#top-link").href = brief.topStory.url;
  document.querySelector("#latest-title").textContent = activeMode === "weekly" ? "Stack signals" : "Latest signals";
  document.querySelector("#listen-title").textContent = activeMode === "weekly" ? "This Week in Tech" : "Today in Tech";
  document.querySelector("#episode-meta").textContent = `English voice · ${brief.episodeLength} min · ${prettyDate(brief.generatedAt)}`;
  const audio = document.querySelector("#episode-audio");
  audio.src = activeMode === "weekly" ? "data/weekly.mp3" : "data/today.mp3";
  audio.load();
  const curiosity = brief.curiosity;
  const curiositySection = document.querySelector("#curiosity-section");
  curiositySection.hidden = !curiosity;
  if (curiosity) {
    document.querySelector("#curiosity-title").textContent = curiosity.title;
    document.querySelector("#curiosity-description").textContent = curiosity.description;
    document.querySelector("#curiosity-link").href = curiosity.url;
  }
  renderCategories();
  renderStories();
}

function loadBrief() {
  const file = activeMode === "weekly" ? "data/weekly.json" : "data/news.json";
  fetch(file)
  .then((response) => response.json())
  .then(renderBrief)
  .catch(() => { document.querySelector("#top-title").textContent = "Today’s brief will be ready shortly."; });
}

document.querySelectorAll("[data-mode]").forEach((button) => button.addEventListener("click", () => {
  activeMode = button.dataset.mode;
  activeCategory = "All";
  document.querySelectorAll("[data-mode]").forEach((item) => item.classList.toggle("active", item === button));
  loadBrief();
}));

loadBrief();
