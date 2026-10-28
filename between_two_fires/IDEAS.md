# Between Two Fires — HOI4 Hungary Mod Design Ideas

> Status: **idea only**. Nothing is built yet, and every number is a placeholder to
> balance later. The name comes from the Hungarian idiom *két tűz között*, "caught
> between two fires".

## Pitch

Hungary in 1936 is a small, disarmed kingdom with no king, ruled by an admiral with no
navy. It wants back the land it lost at Trianon, and only Germany will help it get it.
Every gain from Berlin makes Hungary more dependent on Berlin, and by 1942 the Regent
knows the war is lost.

This mod is about the **double game**. Hungary pays Germany in loyalty, grain, bauxite
and divisions to keep its independence and its revision gains. At the same time it opens
secret channels to the Allies, and tries to switch sides before Germany notices or the
Red Army arrives. History gives one model of success (Romania, 23 August 1944) and two
of failure (Operation Margarethe, March 1944, and Operation Panzerfaust, October 1944).

Like the Adeptus Astartes mod, it is **decisions first**:

- no focus tree and no map changes. Vanilla Hungary (Death or Dishonor) already covers
  Trianon, the Bled agreement, secret rearmament and the Habsburg path, and this mod
  leaves all of that alone
- decisions, missions, national spirits, dynamic modifiers and country flags
- a few news events for the big moments (Margarethe, the armistice, the coup). That's the
  one difference from the Astartes mod, which has no events
- works for Hungary (`original_tag = HUN`) alongside vanilla or a Hungary focus-tree mod

## Design pillars

1. **Two meters, one country.** *Berlin's Trust* and *Allied Contacts* both matter. Most
   actions raise one and lower the other. The double game is keeping both high at once.
2. **Revision costs independence.** Every border gain from Germany adds to the debt that
   Berlin will call in later.
3. **The exit is the game.** The question isn't whether Germany loses the war but whether
   Hungary gets out in time, and to whom it surrenders.
4. **Preparation beats timing.** Switching sides without preparing the army and the
   capital fails, like it did for Horthy in 1944.

## Core loop

```
            ┌──────────── BERLIN'S TRUST ◄──── comply with German Demands (missions)
            │                  ▲               bauxite and grain deliveries
            │                  │               divisions for the Eastern Front
            ▼                  │
 Request Arbitration ──► border gains ──► more German Demands
 (Vienna Awards)
                                                    trust < 25
                                                        │
 Secret channels ──► ALLIED CONTACTS                    ▼
 (Istanbul, Lisbon,        │                 Margarethe Alarm (mission)
  Bern, Stockholm)         │                        │ timer runs out
     │ lowers trust        ▼                        ▼
     └──────────► Prepare the Switch ──►  OPERATION MARGARETHE (occupation)
                  (army, capital,
                   bridges, radio)
                           │
                           ▼
                  ARMISTICE (West or Moscow) ──► success, or Operation Panzerfaust
```

## Timeline of a typical game

| Year | Milestone |
|---|---|
| 1936 | Vanilla rearmament and the Trianon spirit. First secret contacts through the Rothermere network. |
| 1938 | First Vienna Award: southern Slovakia. The first German Demands appear. |
| 1939 | Carpathian Ruthenia. Join the Anti-Comintern Pact, or refuse and stay neutral. |
| 1940 | Second Vienna Award: northern Transylvania. Tripartite Pact pressure. |
| 1941 | Yugoslavia, then the Eastern Front: send the Mobile Corps, or refuse. |
| 1942 | The Second Army. A new Prime Minister starts the double game for real. |
| 1943 | The Don catastrophe risk. Istanbul and the other secret channels. |
| 1944 | Margarethe or the armistice. Prepare the switch, then pick the moment. |
| 1945 | Survive the peace: which borders, and whose sphere. |

---

## The meters

Both are country variables, shown in every decision category's description through
scripted localisation, the same way the Astartes mod shows gene-seed.

| Meter | Variable | Range | Start | Means |
|---|---|---|---|---|
| **Berlin's Trust** | `btf_trust` | 0–100 | 50 | how far Germany tolerates and relies on Hungary |
| **Allied Contacts** | `btf_contacts` | 0–100 | 5 | how far secret talks with the Allies have got |

**Thresholds**

| Trust | Effect |
|---|---|
| ≥ 70 | *Brothers in Arms* spirit: German equipment deliveries, cheaper German licences |
| ≥ 50 | Arbitration requests (Vienna Awards) are available |
| < 50 | German Demands come faster (cooldown −30 days) |
| < 25 | *Margarethe Alarm* mission starts |

| Contacts | Effect |
|---|---|
| ≥ 25 | the Allies stop treating Hungary as a core Axis member (small opinion bonus) |
| ≥ 50 | *Armistice* decisions become visible |
| ≥ 75 | better armistice terms: keep one revision gain, Allied guarantee |

**Drift.** Trust falls by 1 a month while Germany is at war and Hungary isn't fighting
beside it. Contacts fall by 1 a month while Hungary fights the Western Allies. Contacts
don't drift otherwise, so early contacts are an investment.

**Without Germany.** If Germany isn't fascist, doesn't exist or isn't at war by 1941, the
meters freeze, the German Demands stop, and only the revision decisions stay (with a
fallback arbiter: Italy). The mod should never force the historical war.

---

## Decisions

There are five categories.

### 1. Nem, nem, soha! — Revision (visible from game start)

The category is named after the interwar revisionist slogan ("No, no, never!"). Each
arbitration decision transfers vanilla core or claim states. It's only available while the
target still owns them, so it doesn't double up if a vanilla focus or event already
handed them over.

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Justice for Hungary** *(once)* | 25 PP | — | the Rothermere campaign: +5 contacts, small British opinion bonus |
| **Request Arbitration: Upper Hungary** | 50 PP | 1938+; trust ≥ 50; Czechoslovakia exists | First Vienna Award: southern Slovakia; +10 trust; adds one German Demand |
| **Occupy Carpathian Ruthenia** | 50 PP | First Award done; Czechoslovakia breaking up or gone | the state; +5 trust; adds one German Demand |
| **Request Arbitration: Transylvania** | 75 PP | 1940+; trust ≥ 60; Romania not in the Allies | Second Vienna Award: northern Transylvania; +10 trust; Romania gets a hostile *Lost Transylvania* spirit; adds two German Demands |
| **Reclaim the Délvidék** | 50 PP | Yugoslavia at war with Germany or collapsed | Bácska and Baranya; −10 contacts (breaking the 1940 friendship treaty); +5 trust |
| **Honour the Treaty of Eternal Friendship** *(alternative to the above)* | — | Yugoslavia at war with Germany | refuse to join the invasion: +15 contacts, −15 trust. This is what Teleki wanted: he killed himself on 3 April 1941 rather than break the treaty, and Hungary invaded anyway. |

### 2. The Axis Ledger (visible from game start)

These are the ways to *raise* trust. Most cost something Hungary will miss later.

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **Bauxite for Berlin** *(repeatable, 90-day cooldown)* | — | Hungary owns aluminium | exports 50% of aluminium to Germany for 90 days; +5 trust; small PP refund |
| **Grain Deliveries** *(repeatable, 90-day cooldown)* | +15% consumer goods for 90 days | — | +3 trust |
| **German Licence** *(one each: tanks, aircraft, small arms)* | 50 PP | trust ≥ 40 | research bonus for that category; +3 trust; +1 *Dependency* (see below) |
| **Swedish or Italian Licence** *(one each: tanks, aircraft, small arms)* | 75 PP | that country exists and isn't hostile | the same research bonus; no trust change; no Dependency. Historically the Toldi came from Sweden's Landsverk and the Héja from Italy's Reggiane. |
| **Send the Mobile Corps** *(once)* | 4 divisions' equipment, 25k manpower | at war with the Soviet Union | +15 trust; temporary *Expeditionary Losses* spirit |
| **Send the Second Army** *(once)* | 10 divisions' equipment, 100k manpower | Mobile Corps sent; 1942+ | +25 trust; starts the *Don Front* mission |
| **Purge the Anglophiles** | 50 PP | trust < 50 | +10 trust; −10 contacts; −stability |

**Dependency** (`btf_dependency`) counts German licences and deliveries. Each point makes
Operation Margarethe faster (see category 5) and raises the price of the German Demands,
so arming through Germany is quick now and expensive later.

**Don Front** is a mission, not a choice. It runs 120 days; if Germany and its allies
control fewer Soviet states at the end than at the start, the *Catastrophe at the Don* event
removes most of that equipment and manpower and gives −stability and −war support.
Otherwise the army comes home with experience. This replaces the vague history ("Hungary
lost an army") with a risk the player can read.

### 3. German Demands (missions)

These missions are the price of trust, the way the lineage flaws are the price of a
lineage in the Astartes mod. One fires every 150 days (120 below 50 trust) while
Hungary is in Germany's faction or has taken a Vienna Award. Each has a timer: comply in
time for a small trust gain, or let it run out for a large trust loss.

| Mission | Comply with | Timer | If it runs out |
|---|---|---|---|
| **Join the Anti-Comintern Pact** | the decision itself (flag) | 90 days | −15 trust |
| **Leave the League of Nations** | 25 PP | 60 days | −10 trust |
| **Transit Rights** | military access for Germany | 60 days | −15 trust |
| **More Divisions for the East** | Mobile Corps or Second Army sent | 120 days | −20 trust |
| **Raise the Quotas** | two Bauxite or Grain deliveries | 90 days | −10 trust |
| **Dismiss the Prime Minister** *(only with contacts ≥ 40)* | 100 PP and −10 contacts | 60 days | −25 trust (historically Germany demanded Kállay's removal) |

### 4. Secret Channels (visible from 1941, or once contacts ≥ 15)

Each channel is a repeatable decision with a cooldown. They raise contacts and lower
trust: the trust loss is the risk that Germany finds out. Running them while trust is
high is safer.

| Decision | Cost | Requires | Effect |
|---|---|---|---|
| **The Istanbul Channel** *(120-day cooldown)* | 50 PP | — | +15 contacts, −8 trust |
| **The Lisbon Channel** *(120-day cooldown)* | 50 PP | Portugal neutral | +10 contacts, −5 trust |
| **The Bern Channel** *(120-day cooldown)* | 50 PP | Switzerland neutral | +10 contacts, −5 trust |
| **The Stockholm Channel** *(120-day cooldown)* | 50 PP | Sweden neutral | +8 contacts, −3 trust |
| **Send Szent-Györgyi to Istanbul** *(once)* | 25 PP | 1943+ | +20 contacts, −15 trust. Albert Szent-Györgyi, the Nobel laureate, really did carry peace feelers in 1943, and Hitler demanded his arrest. |
| **Don't Shoot at Allied Bombers** *(once)* | — | at war with the Western Allies | +10 contacts; 30 days later Germany notices: −10 trust |
| **Cover Story** *(180-day cooldown)* | 30 PP | — | halves the trust loss of the next channel |

### 5. The Exit (visible once contacts ≥ 50, or the Margarethe Alarm starts)

#### Preparing the switch

Each preparation is a one-off decision that adds 1 to `btf_preparation` (0–5). The
armistice rolls for a coup (see below), and every point of preparation lowers the odds.
Historically, Horthy prepared none of these, and that's why 15 October 1944 failed.

| Preparation | Cost | Effect beyond +1 preparation |
|---|---|---|
| **Brief the Army Commanders** | 50 PP | the army follows the Regent's order |
| **Loyal Divisions to Budapest** | needs 3 divisions in the capital's state | the capital holds against a German coup |
| **Secure the Danube Bridges** | 25 PP, 2 divisions on the Danube | supply into Budapest holds |
| **Seize the Radio Station** | 25 PP | the proclamation reaches the army in time |
| **Arrest the Arrow Cross Leadership** | 50 PP, −stability | removes the coup's leader; −10 trust |

#### Two ways out

| Decision | Requires | Effect |
|---|---|---|
| **Armistice with the Western Allies** | contacts ≥ 50; a Western Allied army controls a state bordering Hungary | leave the Axis, join the Allies; war with Germany; Western sphere after the war. Contacts ≥ 75: keep one revision gain and get an Allied guarantee |
| **Armistice with Moscow** | contacts ≥ 50, or the Red Army controls a state bordering Hungary | leave the Axis, peace with the Soviet Union; war with Germany; +communism support; return to 1937 borders |

The dilemma is the history: the Western option is better, but the Western armies may
never reach the border. Moscow's terms are easier to get, and always worse.

**The coup roll.** When an armistice fires, `random_list` decides between success and
*Operation Panzerfaust*. The odds start at 20% success and rise by 16% per point of
preparation, so full preparation is a sure thing. The decision's tooltip shows the odds.
*Panzerfaust* means a German-backed Arrow Cross government takes over: Hungary becomes a
German puppet, the player keeps playing as that government, and the armistice is lost.

#### Operation Margarethe

The *Margarethe Alarm* mission starts when trust drops below 25. The player has 90 days
(−10 per Dependency point, minimum 30) to raise trust back above 25.

| If the timer runs out with… | Result |
|---|---|
| preparation ≤ 2 | **peaceful occupation**: Hungary becomes a German puppet with an *Occupied Kingdom* spirit; contacts reset to 0 |
| preparation ≥ 3 | **resistance**: Germany declares war; Hungary may join the Allies at once (Western or Moscow terms, whichever is available). Harder than an armistice, but the player keeps control |

#### Armed neutrality (Teleki's path)

A player who never joins Germany's faction and never takes an arbitration can stay out.
German Demands still come (fewer of them), and Margarethe is still possible, but if
Hungary reaches 1945 with trust ≥ 25 and no war against the Allies, it gets the
*Survivor* spirit and the best post-war standing. It costs every revision gain.

---

## National spirits

| Spirit | Source | Effect |
|---|---|---|
| **Brothers in Arms** | trust ≥ 70 | +division attack when fighting beside Germany; cheaper German licences |
| **Expeditionary Losses** | Mobile Corps or Second Army | −manpower, −war support for a year |
| **Catastrophe at the Don** | the *Don Front* mission fails | −stability, −war support, −recruitable population |
| **The Double Game** | contacts ≥ 25 while in the Axis | +political power, −war support (the government doesn't believe in the war) |
| **Occupied Kingdom** | Margarethe | puppet spirit, −stability, −political power |
| **Survivor** | armed neutrality to 1945 | +stability, +political power |

## AI

- AI Hungary follows history by default: takes the awards, sends the Mobile Corps and
  Second Army, opens the Istanbul channel in 1943, and rarely prepares.
- With non-historical AI (the vanilla game rule), it weighs the exit by its contacts and
  by whose army is closest to its border.
- AI Germany doesn't need new logic: the missions and their timeouts act for it.

## Balance guardrails

- **Trust and contacts move in steps of 3–25.** The meters must feel like they move,
  but no single decision should cross a threshold on its own.
- **The western armistice is rare on purpose.** It needs Western troops in the Balkans or
  Austria. If it turns out to be impossible in most games, lower its requirement to
  "Western Allied army within N states" instead of "bordering".
- **Margarethe must be avoidable but costly to avoid.** A player who complies with every
  demand should never see it, but will lose an army at the Don.
- **Don't stack vanilla's Trianon.** Vanilla already models Trianon and the Bled
  agreement. This mod adds no rearmament modifiers of its own; it only prices *who*
  Hungary rearms with.

---

## Minimum viable version

- **Meters:** trust and contacts, with scripted localisation in the category descriptions.
- **Decisions (12):** Justice for Hungary; the Upper Hungary and Transylvania
  arbitrations; Bauxite for Berlin; Send the Mobile Corps; Send the Second Army; the
  Istanbul and Lisbon channels; Brief the Army Commanders, Loyal Divisions to Budapest;
  the two armistices.
- **Missions (4):** Join the Anti-Comintern Pact, More Divisions for the East, Don Front,
  Margarethe Alarm.
- **Events (3 news events):** Operation Margarethe, the armistice, Operation Panzerfaust.
- **Spirits (3):** Brothers in Arms, Catastrophe at the Don, Occupied Kingdom.

Everything else (the other channels, the coup preparations beyond two, armed neutrality,
Dependency) is v0.2.

## Implementation notes

- Prefix every key with `btf_`. Vanilla uses `HUN_` for its own Hungary content, so
  `btf_` keeps clear of it and of other Hungary mods.
- Gate every decision category with `allowed = { original_tag = HUN }`.
- Files:
  - `common/decisions/btf_decisions.txt` and `common/decisions/categories/btf_categories.txt`
  - `common/ideas/btf_spirits.txt`
  - `common/scripted_effects/btf_meters.txt` (`btf_add_trust`, `btf_add_contacts`:
    clamp to 0–100 and check the thresholds in one place)
  - `common/scripted_localisation/btf_meters.txt` (meter text with colour by threshold)
  - `common/on_actions/btf_on_actions.txt` (monthly drift and the German Demand timer)
  - `events/btf_news.txt` (the news events)
  - `localisation/english/btf_l_english.yml`
- The Vienna Award decisions must check state ownership, not just flags, so they stay
  correct whether vanilla's focuses ran or not.
- Before building, read vanilla's Hungary files (its focus tree in `common/national_focus/`,
  the Death or Dishonor events and the starting ideas) to find anything that already moves
  the same states or uses the same historical moments, and gate around it.
- The Astartes mod's `tools/check_mod.py` could be generalised to check this mod too.

---

## Open questions

1. **Folder.** This design lives in `between_two_fires/` inside the Astartes repo for now.
   The game ignores the folder, but a built mod needs its own folder and descriptor, and
   probably its own repository.
2. **Decisions only, or a focus tree?** This design keeps vanilla's tree. A full
   replacement tree would allow more (a Kállay branch, a Teleki branch) but would conflict
   with other Hungary mods and need much more work.
3. **Target version and DLC.** Assume Death or Dishonor (vanilla's Hungary tree)? It
   matters for which states vanilla already moves and which spirits it already uses.
4. **The Arrow Cross government.** After Panzerfaust, should the player keep playing a
   puppet, or should the game end the Hungarian story there? Either way, follow vanilla's
   convention and leave the persecution of Hungary's Jews out of the gameplay, rather
   than turning it into a mechanic.
