const categories = ["All", "AI", "Dev", "Hardware", "Security", "Startups"];
let activeCategory = "All";
let stories = [];

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
      <p>${story.description}</p><span class="story-meta">${story.category} · ${story.source}</span></div>
    </article>`).join("") || "<p>No stories in this category today.</p>";
}

fetch("data/news.json")
  .then((response) => response.json())
  .then((brief) => {
    stories = brief.stories;
    document.querySelector("#brief-date").textContent = prettyDate(brief.generatedAt);
    document.querySelector("#top-title").textContent = brief.topStory.title;
    document.querySelector("#top-description").textContent = brief.topStory.description;
    document.querySelector("#top-link").href = brief.topStory.url;
    document.querySelector("#episode-meta").textContent = `English voice · ${brief.episodeLength} min · ${prettyDate(brief.generatedAt)}`;
    renderCategories();
    renderStories();
  })
  .catch(() => { document.querySelector("#top-title").textContent = "Today’s brief will be ready shortly."; });
