/**
 * Client-side ports of the Python logic modules.
 * Used for static hosting (GitHub Pages); Flask /api/* remains for local Python runs.
 */
(function (global) {
  'use strict';

  function assetUrl(relativePath) {
    const scripts = document.querySelectorAll('script[src]');
    let base = './';
    for (const s of scripts) {
      if (s.src && s.src.includes('modules.js')) {
        base = s.src.replace(/js\/modules\.js(\?.*)?$/, '');
        break;
      }
    }
    return base + relativePath.replace(/^\//, '');
  }

  let zipDatabase = null;
  let zipLoadPromise = null;

  function loadZipDatabase() {
    if (zipDatabase) return Promise.resolve(zipDatabase);
    if (zipLoadPromise) return zipLoadPromise;
    zipLoadPromise = fetch(assetUrl('data/map_data.json'))
      .then((r) => {
        if (!r.ok) throw new Error('Failed to load hazard data');
        return r.json();
      })
      .then((data) => {
        zipDatabase = data;
        return data;
      })
      .catch((err) => {
        zipLoadPromise = null;
        throw err;
      });
    return zipLoadPromise;
  }

  function fmtMoney(n) {
    return n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  const PARTNERS = [
    { name: 'Kitab Cafe', type: 'Bookstore & Cafe', impact: '3 Youth Literacy Events', loc: 'Detroit, MI' },
    { name: 'Cannelle Detroit', type: 'Patisserie & Cafe', impact: 'Senior Outreach Sponsor', loc: 'Detroit, MI' },
    { name: 'A Taste of Marrakech', type: 'Moroccan Culinary', impact: 'Volunteer Catering Partner', loc: 'Dearborn, MI' },
    { name: 'Uyu Coffee', type: 'Specialty Coffee Shop', impact: 'Student Organizer Hub', loc: 'Detroit, MI' },
    { name: 'Cafe Sous Terre', type: 'Neighborhood Cafe', impact: 'Hosted 2 Policy Roundtables', loc: 'Detroit, MI' },
    { name: 'Zamzam Grocers', type: 'Grocery & Halal Butcher', impact: 'Food Security Partner', loc: 'Hamtramck, MI' },
    { name: 'Noor Textiles', type: 'Clothing & Tailoring', impact: 'Job Training Sponsor', loc: 'Dearborn, MI' },
  ];

  const MYTHS = [
    {
      title: 'Banning corporate money isolates a campaign.',
      fact: "Dr. El-Sayed's campaigns successfully raise millions derived entirely from small-dollar grassroots contributions. People-powered > corporate-powered.",
    },
    {
      title: 'Medicare for All expands bureaucratic cost.',
      fact: 'Over 30% of standard health expenditures are eaten by private insurance claims-processing walls. Single-payer eliminates that entirely — less bureaucracy, not more.',
    },
    {
      title: 'A Green New Deal is too expensive.',
      fact: 'The cost of inaction on climate change far exceeds the investment. Lead pipe removal alone saves $188B in healthcare costs over 20 years.',
    },
    {
      title: "Small-dollar campaigns can't compete nationally.",
      fact: 'In 2024, grassroots-funded candidates outperformed PAC-funded opponents in 73% of tested districts. People, not billionaires, decide elections.',
    },
  ];

  const SENIOR_POLICIES = [
    { id: '1', title: 'Housing Stability', impact: 'Capping property tax increases for residents 65+. No senior should lose their home to rising taxes.' },
    { id: '2', title: 'Public Transit', impact: 'New seating and increased frequency on key senior routes. Transportation is a right, not a privilege.' },
    { id: '3', title: 'Healthcare Support', impact: 'Direct connection to low-cost prescription clinics. No senior should skip medication due to cost.' },
    { id: '4', title: 'Community Access', impact: 'Senior-only digital literacy workshops. Bridging the technology gap for our elders.' },
    { id: '5', title: 'Meal Delivery', impact: 'Expanded home-delivered meal programs for homebound seniors. Nutrition is dignity.' },
    { id: '6', title: 'Social Connection', impact: "Funded community center programs for seniors. Loneliness is a health crisis — we're solving it." },
  ];

  const SENIOR_STORIES = [
    { name: 'Martha, 72', location: 'Detroit', story: 'The property tax cap saved my home. I can finally afford my medication.' },
    { name: 'James, 78', location: 'Flint', story: 'The new bus routes mean I can see my grandchildren every Sunday.' },
    { name: 'Eleanor, 81', location: 'Grand Rapids', story: 'The digital workshop taught me to video call my daughter in Chicago. I cry every time.' },
  ];

  const YOUTH_ORGS = [
    { name: 'Detroit Youth Collective', type: 'Mentorship Hub', impact: '120 students mentored in 2025', urgency: 'Critical' },
    { name: 'Dearborn Youth Council', type: 'Civic Engagement', impact: 'Led 3 city council advocacy campaigns', urgency: 'High' },
    { name: 'Flint Youth Media Lab', type: 'Digital Arts', impact: 'Produced 8 student documentaries', urgency: 'Active' },
    { name: 'Hamtramck Youth Initiative', type: 'Community Garden', impact: 'Built 12 urban garden plots', urgency: 'Active' },
    { name: 'Grand Rapids Youth Radio', type: 'Media & Journalism', impact: 'Weekly broadcast on WYCE 88.1 FM', urgency: 'High' },
  ];

  const VAULT = {
    LORE: [
      'The campaign logo was inspired by a 1970s Detroit transit map.',
      'Abdul once debated a squirrel on economic policy for 20 minutes.',
      "The 'Youth Amanah' module code is hidden behind a poem about the riverfront.",
      "There is a hidden command to turn the entire site into 'Dark Mode'.",
      'A time capsule is buried under the campaign headquarters parking lot.',
      'The policy database runs on a repurposed PlayStation 3.',
    ],
    SYSTEM_STATUS: [
      'Servers running at 110% capacity. Cooling fans are screaming.',
      'Detected unauthorized access to the Treasury model. Good luck.',
      "The simulated 'Halal Economy' is currently outperforming reality.",
      'Neural network has started writing its own campaign speeches.',
      'Quantum encryption layer: ACTIVE. NSA decryption estimate: 42 years.',
      'Backup battery: powered by a hamster wheel. Hamster is unionizing.',
    ],
    STAFF_SECRETS: [
      'Campaign Manager is secretly a competitive bird-watcher.',
      'Design lead has a secret stash of emergency snacks in the server room.',
      "Every policy document has at least one typo that acts as a watermarked 'trap'.",
      'The interns are technically running the world.',
      'Chief Strategist writes policy drafts as rap lyrics first, then translates.',
      'Outdated: Coffee machine has been promoted to Junior Policy Advisor.',
    ],
    HIDDEN_POLICY: [
      'Proposing free coffee for every citizen within 5 miles of a library.',
      "Declaring the last Friday of every month 'Pizza Diplomacy Day'.",
      'Mandatory 15-minute nap time for all district officials.',
      'Establishing a formal alliance with the local neighborhood cats.',
      'Requiring all committee meetings to include a Lego-building exercise.',
      'Proposal to replace congressional ties with bow ties. Mandatory.',
    ],
  };

  const runners = {
    endorsement_engine(params) {
      const topic = (params.topic || '').trim();
      if (!topic) {
        return (
          '--- ALGORITHMIC ENDORSEMENT ENGINE ---\n' +
          'Status: Awaiting user profile data...\n' +
          'Enter your primary concern to receive a tailored policy trajectory: ?topic=education\n'
        );
      }
      const data = {
        healthcare: 'Single-payer framework detected. Removing private insurance bloat by 30%.',
        housing: 'Stabilization protocol engaged. Tax caps for 65+ residents initiated.',
        transit: 'Expansion logic active. Increasing frequency on high-density corridors.',
        goldensun: 'SYSTEM OVERRIDE: Favorite game detected. Logic suggests: The best solutions are found through ancient wisdom and modern resolve.',
        default: "Data point recognized. Policy white-paper: 'Universal Dignity' is currently being drafted for this category.",
      };
      const result = data[topic.toLowerCase()] || data.default;
      return (
        `--- ANALYSIS FOR: ${topic.toUpperCase()} ---\n` +
        `ENGINE RESPONSE: ${result}\n\n` +
        'Confidence Score: 99.9% (Calculated via grassroots sentiment).'
      );
    },

    financial_simulator(params) {
      const { budget, income, growth, years } = params;
      if (budget == null || budget === '' || income == null || income === '') {
        return (
          '--- FINANCIAL SIMULATOR ---\n' +
          'Welcome to the Policy-Impact Calculator.\n\n' +
          "This tool compares Abdul's proposed economic model against\n" +
          'corporate benchmarks in real time.\n\n' +
          'Enter your financial variables:\n' +
          '  ?budget=500   (base cost in $)\n' +
          '  ?income=75000 (annual income in $)\n' +
          '  ?growth=1.05  (optional growth multiplier)\n' +
          '  ?years=3      (optional projection years)\n\n' +
          'Example: /financial?budget=500&income=75000'
        );
      }
      const b = Number(budget);
      const i = Number(income);
      if (!Number.isFinite(b) || !Number.isFinite(i)) {
        return "ERROR: 'budget' and 'income' must be numeric values.";
      }
      const corporate_model = b * 1.25;
      const abdul_model = b * 0.6;
      const savings = corporate_model - abdul_model;
      const rate = i <= 50000 ? 0.02 : 0.085;
      const contribution = i * rate;

      let projected_savings = null;
      let g;
      let y;
      if (growth !== undefined && growth !== null && growth !== '') {
        g = Number(growth);
        y = years ? parseInt(years, 10) : 1;
        if (Number.isFinite(g) && Number.isFinite(y)) {
          projected_savings = savings * Math.pow(1 + g, y);
        }
      }

      const lines = [
        '╔══════════════════════════════════════════╗',
        '║        FINANCIAL IMPACT DASHBOARD        ║',
        '╚══════════════════════════════════════════╝',
        '',
        `  Base Cost : $${fmtMoney(b)}`,
        `  Income    : $${fmtMoney(i)}`,
        '',
        '  ── Inflation Model Comparison ──',
        `  Corporate Model : $${fmtMoney(corporate_model)}`,
        `  Abdul's Model   : $${fmtMoney(abdul_model)}`,
        `  YOU SAVE        : $${fmtMoney(savings)}`,
        '',
        '  ── Tax Contribution ──',
        `  Rate            : ${(rate * 100).toFixed(1)}%`,
        `  Contribution    : $${fmtMoney(contribution)}`,
      ];
      if (projected_savings != null) {
        lines.push(
          '',
          '  ── Growth Projection ──',
          `  Multiplier      : ${(g * 100).toFixed(1)}%`,
          `  Span            : ${y} year(s)`,
          `  Projected Value : $${fmtMoney(projected_savings)}`
        );
      }
      lines.push('', '  ⚡ Status: Policy impact calculated live.');
      return lines.join('\n');
    },

    tax_calculator(params) {
      const { base, income } = params;
      if (base == null || base === '' || income == null || income === '') {
        return (
          '--- INTERACTIVE FINANCIAL CALCULATOR ---\n' +
          'Status: Awaiting input parameters.\n\n' +
          "USAGE: Append '?base=1000&income=75000' to the URL.\n" +
          'Example: /tax?base=500&income=50000'
        );
      }
      const b = Number(base);
      const i = Number(income);
      if (!Number.isFinite(b) || !Number.isFinite(i)) {
        return "ERROR: Please provide numeric values for 'base' and 'income'.";
      }
      const corporate_model = b * 1.25;
      const abdul_model = b * 0.6;
      const savings = corporate_model - abdul_model;
      const rate = i <= 50000 ? 0.02 : 0.085;
      const contribution = i * rate;
      return (
        `--- FINANCIAL IMPACT DASHBOARD ---\n` +
        `Base Cost: $${fmtMoney(b)} | Annual Income: $${fmtMoney(i)}\n\n` +
        `INFLATION SAVINGS (Comparison):\n` +
        ` • Corporate Model : $${fmtMoney(corporate_model)}\n` +
        ` • Abdul's Model   : $${fmtMoney(abdul_model)}\n` +
        ` • TOTAL SAVINGS   : $${fmtMoney(savings)}\n\n` +
        `TAX CALCULATION (Progressive):\n` +
        ` • Effective Rate  : ${(rate * 100).toFixed(1)}%\n` +
        ` • Contribution    : $${fmtMoney(contribution)}\n\n` +
        'STATUS: Calibration complete. Calculations are live.'
      );
    },

    async hazard_lookup(params) {
      const val = params.val;
      if (!val) {
        return (
          '--- REGIONAL HAZARD DATABASE ---\n' +
          'System Online. Please provide a 5-digit ZIP code (?val=XXXXX).'
        );
      }
      const db = await loadZipDatabase();
      const zip_code = String(val).trim();
      const info = db[zip_code];
      if (info) {
        return (
          `--- HAZARD REPORT FOR ${zip_code} ---\n` +
          `Location: ${info.locale || 'Unknown'}\n` +
          `Hazard  : ${info.hazard || 'N/A'}\n` +
          `Impact  : ${info.impact || 'N/A'}\n` +
          `Remedy  : ${info.remedy || 'N/A'}\n\n` +
          'Data Source: 2026 Regional Environmental Audit.'
        );
      }
      return (
        `NO DATA FOUND for ZIP ${zip_code}.\n` +
        'If this is a mistake, contact your district data architect.'
      );
    },

    halal_economy(params) {
      const option = params.option;
      const investment = params.investment !== undefined && params.investment !== '' ? params.investment : 50000;

      if (option === '1') {
        const inv = Number(investment);
        if (!Number.isFinite(inv)) return 'ERROR: investment must be numeric.';
        return (
          `--- FINANCING SIMULATOR ---\n` +
          `Target: $${fmtMoney(inv)}\n` +
          `Equity Buy-in: $${fmtMoney(Math.round((inv / 36) * 100) / 100)}/mo (0% Interest)`
        );
      }
      if (option === '2') {
        let output = 'PARTNERED MUSLIM-OWNED BUSINESSES\n' + '='.repeat(60) + '\n';
        PARTNERS.forEach((biz, i) => {
          output += `[${i + 1}] ${biz.name} (${biz.type}) | Impact: ${biz.impact} | Loc: ${biz.loc}\n`;
        });
        output += '='.repeat(60) + '\nTotal Active Network: 35+ District Businesses.';
        return output;
      }
      if (option === '3') {
        return (
          'POLICY BRIEF: The Halal economy creates sustainable local growth ' +
          'by circulating capital within the district. Interest-free financing ' +
          'empowers small businesses and builds community wealth.'
        );
      }
      return (
        '--- HALAL ECONOMY DASHBOARD ---\n' +
        'Select an option:\n' +
        '[1] Financing Simulator\n' +
        '[2] View Partner Network\n' +
        '[3] Read Policy Brief'
      );
    },

    myth_buster() {
      const lines = [
        '╔═══════════════════════════════════════════╗',
        '║            CAMPAIGN MYTH BUSTER           ║',
        '╚═══════════════════════════════════════════╝',
        '',
      ];
      MYTHS.forEach((myth) => {
        lines.push(`  ❓ Q: ${myth.title}`);
        lines.push(`  ✅ A: ${myth.fact}`);
        lines.push('');
      });
      lines.push('─'.repeat(50));
      lines.push(`  Total Myths Busted: ${MYTHS.length}`);
      lines.push('  Status: Truth in progress.');
      return lines.join('\n');
    },

    policy_deep_dive() {
      const policies = {
        '1': {
          title: 'Medicare for All Framework',
          data: 'Comprehensive single-payer architecture. Fully guarantees dental, vision, and mental healthcare with zero cost-sharing at delivery.',
        },
        '2': {
          title: 'Green New Deal Blueprint',
          data: 'Infrastructure grid targeting lead pipe replacement networks and zero-emission municipal logistics across Michigan.',
        },
        '3': {
          title: 'Corporate Super PAC Bans',
          data: 'Absolute ban on individual executive shell entities and campaign asset packaging via corporate lobbyists.',
        },
        '4': {
          title: 'NEW POLICY TITLE',
          data: 'Details about the new policy go here.',
        },
      };
      let output = '='.repeat(60) + '\n';
      output += ' POLICY DEEP DIVE ANALYSIS BACKEND '.padStart(47, '=').padEnd(60, '=') + '\n';
      output += '='.repeat(60) + '\n\n';
      output += 'Select platform structure matrix to unpack:\n\n';
      Object.keys(policies).forEach((key) => {
        output += ` [${key}] ${policies[key].title}\n`;
      });
      output += '\n' + '-'.repeat(60) + '\n';
      output += 'Status: Ready for input.';
      return output;
    },

    senior_engagement() {
      const lines = [
        '╔═══════════════════════════════════════════╗',
        '║  SENIOR ADVOCACY & QUALITY OF LIFE       ║',
        '╚═══════════════════════════════════════════╝',
        '',
        '  ── Policy Commitments ──',
        '',
      ];
      SENIOR_POLICIES.forEach((p) => {
        lines.push(`  [${p.id}] ${p.title}`);
        lines.push(`      ✅ ${p.impact}`);
        lines.push('');
      });
      lines.push('─'.repeat(50));
      lines.push('  ── Real Stories, Real Impact ──');
      lines.push('');
      SENIOR_STORIES.forEach((s) => {
        lines.push(`  👤 ${s.name} — ${s.location}`);
        lines.push(`     "${s.story}"`);
        lines.push('');
      });
      lines.push('─'.repeat(50));
      lines.push(`  Total Policies: ${SENIOR_POLICIES.length}`);
      lines.push('  Constituents Impacted: 12,400+');
      lines.push('  Commitment: Stability, Accessibility, and Health.');
      return lines.join('\n');
    },

    youth_amanah(params) {
      const user_input = params.user_input || '';
      if (user_input && user_input.toLowerCase().includes('help')) {
        return (
          '🔥 YOUTH HELP SYSTEM\n' +
          'If you are a young person in crisis, contact:\n' +
          '  Youth Crisis Line: 1-800-334-HELP\n' +
          '  Campaign Youth Desk: (313) 555-YOUTH'
        );
      }
      const lines = [
        '╔═══════════════════════════════════════════╗',
        '║     YOUTH MOMENTUM TRACKER               ║',
        '╚═══════════════════════════════════════════╝',
        '',
      ];
      YOUTH_ORGS.forEach((org) => {
        let badge = '🌱 ACTIVE';
        if (org.urgency === 'Critical') badge = '🔥 CRITICAL';
        else if (org.urgency === 'High') badge = '⚡ HIGH';
        lines.push(`  ${badge}`);
        lines.push(`  ${org.name.toUpperCase()} (${org.type})`);
        lines.push(`     ${org.impact}`);
        lines.push('');
      });
      lines.push('─'.repeat(50));
      lines.push(`  Tracked Organizations: ${YOUTH_ORGS.length}`);
      lines.push('  Total Youth Impacted: 840+');
      lines.push('  Status: Optimistic. Keep pushing!');
      return lines.join('\n');
    },

    simulation_history(params) {
      const unlock = params.unlock;
      if (unlock === 'abdulwillbenchtovictory26') {
        const keys = Object.keys(VAULT);
        const category = keys[Math.floor(Math.random() * keys.length)];
        const entries = VAULT[category];
        const entry = entries[Math.floor(Math.random() * entries.length)];
        const catPad = (category + '                               ').slice(0, 31);
        return (
          '╔═══════════════════════════════════════════╗\n' +
          '║  🔓 CLASSIFIED ARCHIVE UNLOCKED          ║\n' +
          `║  CATEGORY: ${catPad} ║\n` +
          '╚═══════════════════════════════════════════╝\n\n' +
          `  ${entry}\n\n` +
          '  ─── Decryption: Complete ───'
        );
      }
      if (unlock) {
        return (
          '╔═══════════════════════════════════════════╗\n' +
          '║  🚫 ACCESS DENIED                        ║\n' +
          '╚═══════════════════════════════════════════╝\n\n' +
          `  Key '${unlock}' is invalid.\n` +
          "  Hint: Try the campaign's launch year key."
        );
      }
      return (
        '╔═══════════════════════════════════════════╗\n' +
        '║  📦 ARCHIVE STATUS: SEALED               ║\n' +
        '╚═══════════════════════════════════════════╝\n\n' +
        '  The classified simulation archive is\n' +
        '  encrypted and locked.\n\n' +
        '  To access, provide an unlock code:\n' +
        '  ?unlock=XXXXXXXXXX\n\n' +
        '  Categories locked inside:\n' +
        `    📜 Lore (${VAULT.LORE.length} entries)\n` +
        `    ⚙️  System Statuses (${VAULT.SYSTEM_STATUS.length} entries)\n` +
        `    🤫 Staff Secrets (${VAULT.STAFF_SECRETS.length} entries)\n` +
        `    📋 Hidden Policies (${VAULT.HIDDEN_POLICY.length} entries)\n`
      );
    },
  };

  async function run(moduleName, params) {
    const fn = runners[moduleName];
    if (!fn) throw new Error(`Unknown module: ${moduleName}`);
    return await fn(params || {});
  }

  global.BottomlineModules = { run, runners };
})(typeof window !== 'undefined' ? window : globalThis);
