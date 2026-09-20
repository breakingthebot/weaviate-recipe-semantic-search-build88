/**
 * Build 88 — Weaviate Recipe Semantic Search Engine Frontend Controller
 * Manages tab switching, sensory nearText search, hybrid blending, chef recommendations,
 * and live Weaviate class schema telemetry.
 */

// --------------------------------------------------------------------------
// DOM Element References
// --------------------------------------------------------------------------
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Header Telemetry & Buttons
const topRecipeCount = document.getElementById('top-recipe-count');
const btnResetIndex = document.getElementById('btn-reset-index');
const btnReseedCatalog = document.getElementById('btn-reseed-catalog');

// Semantic Search Controls
const formSemanticSearch = document.getElementById('form-semantic-search');
const semanticQueryInput = document.getElementById('semantic-query');
const filterCuisine = document.getElementById('filter-cuisine');
const filterDietary = document.getElementById('filter-dietary');
const filterCertainty = document.getElementById('filter-certainty');
const valCertainty = document.getElementById('val-certainty');
const semanticResultsGrid = document.getElementById('semantic-results-grid');
const semanticResultsMeta = document.getElementById('semantic-results-meta');
const resultsCountLabel = document.getElementById('results-count-label');
const resultsTimeLabel = document.getElementById('results-time-label');
const quickPills = document.querySelectorAll('.pill-btn');

// Hybrid Search Controls
const formHybridSearch = document.getElementById('form-hybrid-search');
const hybridQueryInput = document.getElementById('hybrid-query');
const hybridAlphaInput = document.getElementById('hybrid-alpha');
const valHybridAlpha = document.getElementById('val-hybrid-alpha');
const hybridAlphaStatus = document.getElementById('hybrid-alpha-status');
const hybridLimitInput = document.getElementById('hybrid-limit');
const valHybridLimit = document.getElementById('val-hybrid-limit');
const hybridResultsBox = document.getElementById('hybrid-results-box');

// Chef Recommendation Controls
const formChef = document.getElementById('form-chef');
const chefCravingInput = document.getElementById('chef-craving');
const chefDietarySelect = document.getElementById('chef-dietary');
const chefMaxTimeInput = document.getElementById('chef-max-time');
const chefOutputBox = document.getElementById('chef-output-box');
const chefRecTitle = document.getElementById('chef-rec-title');
const chefRecCuisine = document.getElementById('chef-rec-cuisine');
const chefRecConfidence = document.getElementById('chef-rec-confidence');
const chefRecRationale = document.getElementById('chef-rec-rationale');
const chefRecPairing = document.getElementById('chef-rec-pairing');
const chefRecSubs = document.getElementById('chef-rec-subs');

// Recipe Creation & Schema Controls
const formCreateRecipe = document.getElementById('form-create-recipe');
const schemaClassName = document.getElementById('schema-class-name');
const schemaIndexType = document.getElementById('schema-index-type');
const schemaMetric = document.getElementById('schema-metric');
const schemaObjectsCount = document.getElementById('schema-objects-count');
const schemaPropertiesBody = document.getElementById('schema-properties-body');

// --------------------------------------------------------------------------
// Notification Toast Utility
// --------------------------------------------------------------------------
function showToast(message) {
  const existing = document.querySelector('.toast-msg');
  if (existing) {
    existing.remove();
  }
  const toast = document.createElement('div');
  toast.className = 'toast-msg';
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => {
      toast.remove();
    }, 300);
  }, 3500);
}

// --------------------------------------------------------------------------
// Navigation Tab Switching
// --------------------------------------------------------------------------
tabButtons.forEach(button => {
  button.addEventListener('click', () => {
    const targetTabId = button.getAttribute('data-tab');
    
    // Update active tab button state
    tabButtons.forEach(btn => {
      btn.classList.remove('active');
    });
    button.classList.add('active');

    // Show selected section
    tabContents.forEach(content => {
      content.classList.remove('active');
      if (content.id === targetTabId) {
        content.classList.add('active');
      }
    });

    // Refresh schema when entering schema tab
    if (targetTabId === 'tab-schema') {
      fetchSchemaTelemetry();
    }
  });
});

// --------------------------------------------------------------------------
// Range Slider Value Updaters
// --------------------------------------------------------------------------
filterCertainty.addEventListener('input', () => {
  valCertainty.textContent = Number(filterCertainty.value).toFixed(2);
});

hybridAlphaInput.addEventListener('input', () => {
  const alpha = Number(hybridAlphaInput.value);
  valHybridAlpha.textContent = alpha.toFixed(2);
  
  if (alpha === 0.0) {
    hybridAlphaStatus.textContent = 'Pure BM25 Exact Keywords (0% Vector)';
  } else if (alpha === 1.0) {
    hybridAlphaStatus.textContent = 'Pure nearText Semantic Vector (0% BM25)';
  } else if (alpha === 0.5) {
    hybridAlphaStatus.textContent = 'Balanced Blending (50% Vector / 50% BM25)';
  } else if (alpha > 0.5) {
    hybridAlphaStatus.textContent = `Vector Dominant (${Math.round(alpha * 100)}% Vector / ${Math.round((1 - alpha) * 100)}% BM25)`;
  } else {
    hybridAlphaStatus.textContent = `Keyword Dominant (${Math.round((1 - alpha) * 100)}% BM25 / ${Math.round(alpha * 100)}% Vector)`;
  }
});

hybridLimitInput.addEventListener('input', () => {
  valHybridLimit.textContent = hybridLimitInput.value;
});

// --------------------------------------------------------------------------
// Quick Preset Suggestion Pills
// --------------------------------------------------------------------------
quickPills.forEach(pill => {
  pill.addEventListener('click', () => {
    const queryText = pill.getAttribute('data-query');
    semanticQueryInput.value = queryText;
    runSemanticSearch();
  });
});

// --------------------------------------------------------------------------
// Fetch Weaviate Schema Telemetry & Metrics
// --------------------------------------------------------------------------
async function fetchSchemaTelemetry() {
  try {
    const response = await fetch('/api/system/schema');
    if (!response.ok) {
      throw new Error(`Failed to load schema: ${response.status}`);
    }
    const data = await response.json();

    schemaClassName.textContent = data.class_name;
    schemaIndexType.textContent = data.vector_index_type.toUpperCase();
    schemaMetric.textContent = data.distance_metric;
    schemaObjectsCount.textContent = data.total_objects;
    topRecipeCount.textContent = `${data.total_objects} Recipes`;

    schemaPropertiesBody.innerHTML = '';
    data.properties.forEach(prop => {
      const tr = document.createElement('tr');
      const dataTypeStr = Array.isArray(prop.dataType) ? prop.dataType.join(', ') : (prop.dataType || 'text');
      tr.innerHTML = `
        <td class="prop-name">${prop.name}</td>
        <td class="prop-type">${dataTypeStr}</td>
        <td>${prop.description}</td>
      `;
      schemaPropertiesBody.appendChild(tr);
    });
  } catch (err) {
    console.error('Error loading schema telemetry:', err);
  }
}

// --------------------------------------------------------------------------
// Render Recipe Cards Helper
// --------------------------------------------------------------------------
function renderRecipeCard(match) {
  const recipe = match.recipe;
  const certaintyPercent = Math.round(match.certainty * 100);
  const distanceFormatted = match.distance.toFixed(4);

  const card = document.createElement('div');
  card.className = 'recipe-card';

  const dietaryTagsHtml = (recipe.dietary_tags || [])
    .map(tag => `<span class="badge badge-cuisine">${tag}</span>`)
    .join('');

  const ingredientsHtml = (recipe.ingredients || [])
    .slice(0, 6)
    .map(ing => `<span class="ingredient-tag">${ing}</span>`)
    .join('');

  card.innerHTML = `
    <div class="recipe-card-header">
      <div>
        <h4 class="recipe-title">${recipe.title}</h4>
        <div class="recipe-badges" style="margin-top: 0.375rem;">
          <span class="badge badge-recipes">${recipe.cuisine}</span>
          <span class="badge badge-difficulty">${recipe.difficulty}</span>
          ${dietaryTagsHtml}
        </div>
      </div>
      <div class="recipe-score-badge">
        <span class="certainty-score">${certaintyPercent}% Certainty</span>
        <span class="distance-score">Dist: ${distanceFormatted}</span>
      </div>
    </div>
    
    <p class="recipe-description">${recipe.description}</p>
    
    <div>
      <div style="font-size: 0.6875rem; color: var(--text-muted); text-transform: uppercase;">Key Ingredients:</div>
      <div class="recipe-ingredients-list">${ingredientsHtml}</div>
    </div>

    <div class="recipe-meta-row">
      <span>⏱ Prep: ${recipe.prep_time_minutes}m • Cook: ${recipe.cook_time_minutes}m</span>
      <span>🔥 ${recipe.calories_per_serving} kcal</span>
    </div>
  `;

  return card;
}

// --------------------------------------------------------------------------
// Execute Sensory nearText Search
// --------------------------------------------------------------------------
async function runSemanticSearch() {
  const query = semanticQueryInput.value.trim();
  if (!query) {
    return;
  }

  semanticResultsGrid.innerHTML = '<div class="empty-state">Searching Weaviate semantic flavor space...</div>';

  // Construct optional Weaviate GraphQL where filter
  let whereFilter = null;
  const selectedCuisine = filterCuisine.value;
  const selectedDietary = filterDietary.value;

  if (selectedCuisine && selectedDietary) {
    whereFilter = {
      operator: 'And',
      operands: [
        { operator: 'Equal', path: ['cuisine'], valueText: selectedCuisine },
        { operator: 'ContainsAny', path: ['dietary_tags'], valueText: selectedDietary }
      ]
    };
  } else if (selectedCuisine) {
    whereFilter = {
      operator: 'Equal',
      path: ['cuisine'],
      valueText: selectedCuisine
    };
  } else if (selectedDietary) {
    whereFilter = {
      operator: 'ContainsAny',
      path: ['dietary_tags'],
      valueText: selectedDietary
    };
  }

  const payload = {
    concepts: [query],
    limit: 6,
    certainty: parseFloat(filterCertainty.value),
    where: whereFilter
  };

  try {
    const startTime = performance.now();
    const response = await fetch('/api/search/semantic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Semantic search failed with status ${response.status}`);
    }

    const data = await response.json();
    const results = data.matches || [];
    const endTime = performance.now();
    const elapsed = (endTime - startTime).toFixed(1);

    semanticResultsMeta.style.display = 'flex';
    resultsCountLabel.textContent = `Found ${results.length} matching recipe${results.length === 1 ? '' : 's'}`;
    resultsTimeLabel.textContent = `${elapsed} ms`;

    if (results.length === 0) {
      semanticResultsGrid.innerHTML = `
        <div class="empty-state">
          No recipes met the certainty threshold of ${(payload.certainty * 100).toFixed(0)}% with current filters.
          Try lowering the minimum certainty slider or removing dietary constraints.
        </div>
      `;
      return;
    }

    semanticResultsGrid.innerHTML = '';
    results.forEach(match => {
      const card = renderRecipeCard(match);
      semanticResultsGrid.appendChild(card);
    });
  } catch (err) {
    console.error('Semantic search error:', err);
    semanticResultsGrid.innerHTML = `<div class="empty-state" style="color: #f87171;">Search error: ${err.message}</div>`;
  }
}

formSemanticSearch.addEventListener('submit', (e) => {
  e.preventDefault();
  runSemanticSearch();
});

// --------------------------------------------------------------------------
// Execute Hybrid Search
// --------------------------------------------------------------------------
async function runHybridSearch() {
  const query = hybridQueryInput.value.trim();
  if (!query) {
    return;
  }

  hybridResultsBox.innerHTML = '<div class="empty-state">Blended vector & keyword search in progress...</div>';

  const payload = {
    query: query,
    alpha: parseFloat(hybridAlphaInput.value),
    limit: parseInt(hybridLimitInput.value, 10)
  };

  try {
    const response = await fetch('/api/search/hybrid', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Hybrid search failed: ${response.status}`);
    }

    const data = await response.json();
    const results = data.matches || [];

    if (results.length === 0) {
      hybridResultsBox.innerHTML = '<div class="empty-state">No hybrid matches found for this query.</div>';
      return;
    }

    const grid = document.createElement('div');
    grid.className = 'recipe-grid';

    results.forEach(match => {
      const card = renderRecipeCard(match);
      grid.appendChild(card);
    });

    hybridResultsBox.innerHTML = '';
    hybridResultsBox.appendChild(grid);
  } catch (err) {
    console.error('Hybrid search error:', err);
    hybridResultsBox.innerHTML = `<div class="empty-state" style="color: #f87171;">Search error: ${err.message}</div>`;
  }
}

formHybridSearch.addEventListener('submit', (e) => {
  e.preventDefault();
  runHybridSearch();
});

// --------------------------------------------------------------------------
// Execute Chef & Sommelier Recommendation Engine
// --------------------------------------------------------------------------
async function runChefRecommendation() {
  const craving = chefCravingInput.value.trim();
  if (!craving) {
    return;
  }

  const dietary = chefDietarySelect.value ? [chefDietarySelect.value] : [];
  const maxTime = chefMaxTimeInput.value ? parseInt(chefMaxTimeInput.value, 10) : null;

  const payload = {
    craving_description: craving,
    dietary_restrictions: dietary,
    max_prep_time_minutes: maxTime
  };

  try {
    const response = await fetch('/api/recipes/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Chef recommendation error: ${response.status}`);
    }

    const data = await response.json();

    chefRecTitle.textContent = data.top_recipe.title;
    chefRecCuisine.textContent = data.top_recipe.cuisine;
    chefRecConfidence.textContent = `Confidence: ${Math.round(data.confidence_score * 100)}%`;
    chefRecRationale.textContent = data.recommendation_text;
    chefRecPairing.textContent = data.pairing_suggestion;

    chefRecSubs.innerHTML = '';
    if (data.substitution_tips && data.substitution_tips.length > 0) {
      data.substitution_tips.forEach(sub => {
        const li = document.createElement('li');
        li.textContent = sub;
        chefRecSubs.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.textContent = 'None required — this dish naturally adheres to your taste profile!';
      chefRecSubs.appendChild(li);
    }

    chefOutputBox.style.display = 'block';
    showToast('Chef recommendation generated!');
  } catch (err) {
    console.error('Chef recommendation error:', err);
    showToast(`Error: ${err.message}`);
  }
}

formChef.addEventListener('submit', (e) => {
  e.preventDefault();
  runChefRecommendation();
});

// --------------------------------------------------------------------------
// Create & Index New Recipe
// --------------------------------------------------------------------------
formCreateRecipe.addEventListener('submit', async (e) => {
  e.preventDefault();

  const title = document.getElementById('new-title').value.trim();
  const cuisine = document.getElementById('new-cuisine').value.trim();
  const difficulty = document.getElementById('new-difficulty').value;
  const description = document.getElementById('new-description').value.trim();
  const ingredientsRaw = document.getElementById('new-ingredients').value;
  const dietaryRaw = document.getElementById('new-dietary').value;
  const prep = parseInt(document.getElementById('new-prep').value, 10);
  const cook = parseInt(document.getElementById('new-cook').value, 10);
  const calories = parseInt(document.getElementById('new-calories').value, 10);

  const ingredients = ingredientsRaw.split(',').map(s => s.trim()).filter(Boolean);
  const dietary_tags = dietaryRaw.split(',').map(s => s.trim()).filter(Boolean);

  const payload = {
    title: title,
    cuisine: cuisine,
    description: description,
    ingredients: ingredients,
    dietary_tags: dietary_tags,
    prep_time_minutes: prep,
    cook_time_minutes: cook,
    calories_per_serving: calories,
    difficulty: difficulty
  };

  try {
    const response = await fetch('/api/recipes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`Failed to create recipe: ${response.status}`);
    }

    const data = await response.json();
    showToast(`Indexed "${data.recipe.title}" into Weaviate!`);
    formCreateRecipe.reset();
    fetchSchemaTelemetry();
  } catch (err) {
    console.error('Error creating recipe:', err);
    showToast(`Error: ${err.message}`);
  }
});

// --------------------------------------------------------------------------
// Index Reset & Reseed Operations
// --------------------------------------------------------------------------
btnResetIndex.addEventListener('click', async () => {
  if (!confirm('Are you sure you want to purge all recipes from Weaviate?')) {
    return;
  }

  try {
    const response = await fetch('/api/system/reset', { method: 'POST' });
    if (!response.ok) {
      throw new Error('Failed to reset Weaviate index');
    }
    showToast('Weaviate index purged.');
    fetchSchemaTelemetry();
    semanticResultsGrid.innerHTML = '<div class="empty-state">Index is empty. Click Reseed to load starter recipes.</div>';
  } catch (err) {
    console.error('Reset error:', err);
    showToast(`Error: ${err.message}`);
  }
});

btnReseedCatalog.addEventListener('click', async () => {
  try {
    const response = await fetch('/api/system/seed', { method: 'POST' });
    if (!response.ok) {
      throw new Error('Failed to reseed catalog');
    }
    const data = await response.json();
    showToast(`Catalog reseeded with ${data.seeded_count} recipes!`);
    fetchSchemaTelemetry();
    runSemanticSearch();
  } catch (err) {
    console.error('Reseed error:', err);
    showToast(`Error: ${err.message}`);
  }
});

// --------------------------------------------------------------------------
// Initialization on Document Ready
// --------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  fetchSchemaTelemetry();
  // Auto-run initial semantic search with the default placeholder
  semanticQueryInput.value = 'Comforting creamy garlic dinner for a cold rainy evening';
  runSemanticSearch();
});
