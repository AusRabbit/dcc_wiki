---
title: "Combat"
group: "Game Guide"
type: rule
conf: hi
dek: "They signpost, you react, they hit, you hit back. Two actions each."
---

In most systems you take turns. Here the GM tells you what the enemy is about to do, and you
respond — the way a video game telegraphs an attack, and the way the books work. Every round
you get **two actions**. Each one you spend reacting is one fewer for hitting back.

## The basics

- **Two actions per round**, per crawler. No initiative, and you can't save an action for next round.
- **Step** — every action carries a free step of two squares (10 feet).
- **Move** — 20 feet, four squares. Move plus step is 30 feet, six squares, in one action.
- Each square on the battle map is five feet, so divide every range by five.
- Enemy dice are rolled by the Dungeon AI.

## A round, in five beats

- **1. They signpost** — the GM says what every mob is doing and who it's after.
- **2. You react** — spend actions on interrupts (Evade, Taunt, Heal…) before anything lands.
- **3. They hit** — anything you didn't evade lands. Take off your DR, then mark your health bar.
- **4. You hit back** — spend whatever actions you have left. Attack, cast, move, Call a Play.
- **5. Reset** — everyone back to two actions. Back to beat 1.

## Example: one simple round

- **The GM says:** a goblin throws a boomerang at Darcy, and another swings at Frank.
- **Darcy reacts:** Evade — one action. *(One left.)*
- **Frank reacts:** nothing. He wants both actions for hitting. *(Two left.)*
- **They hit:** Darcy's evade succeeds and he dodges. Frank takes the swing: 6 damage, minus 1 DR, is 5.
- **You hit back:** Darcy shoots with his last action. Frank casts Magic Missile, then swings his paddle.
- **Reset:** both back on two actions. The GM signposts again.

> [!note] The only real decision
> React, or save your actions to hit back. Evading costs you an attack. Not evading costs you
> health. Against goblins it hardly matters. Against something big it decides whether you
> live.

## Interrupts — what you can do before the hits land

All of these come out of your two actions, and they happen in **beat 2**, straight after
the GM signposts.

- **Evade** — one action covers *every* attack aimed at you this round. Roll a separate d20 + Evade for each one.
- **[[skill-taunt|Taunt]]** — pull an attack off a mate and onto yourself. Anyone can try it. See below.
- **[[skill-catcher|Catcher]]** — dive in front of a hit that's already landed on a mate. Needs ranks. See below.
- **Intervene** — after a mate rolls, add 1d6 to their total. Best on a **Near Miss** (fail by 1–2), which the GM will call out so you know to jump in. Works on any d20 check except stat checks.
- **Heal** — every crawler has [[spell-heal|Heal]]: 2 mana for 2 health slots, self only. Cast as an interrupt, it lands *before* the damage does.
- **[[skill-shield-block|Shield Block]]** — needs a shield. Roll against each physical attack, and halve the damage on a success.
- **[[skill-attack-of-opportunity|Attack of Opportunity]]** — needs ranks and a one-handed melee weapon. When a foe moves out of a square next to you (not just a step), spend an action to hit it.

## Taunt

*Charisma, Interrupt.* You shout, swear, and maybe make an obscene hand gesture at
everything within 30 feet.

- **When:** beat 2 only, after you've heard where the attacks are going. It's a reaction. You can't do it in beat 4.
- **Roll:** d20 + Charisma + Taunt rank, against the mob's Int. Untrained, you roll with Disadvantage.
- **Success:** pick one attack aimed at anyone and it comes at you instead. Better results pull more attacks.
- **Then:** spend your other action to Evade the attacks you just pulled, if you like. Or take them on the chin.
- **Rank 5:** you get a free evade against every attack you taunt.

Both of you tried it untrained in [[session-01]] and both missed — Frank shouting *look at
me, you ugly goblins*, Darcy shouting *don't hit my friend*. Both attempts are ticked, so
either of you can keep Taunt at the next safe room ([[levelling-skills]]).

> [!note] Why it matters for you two
> Darcy is the tough one and the better evader. Frank is the glass cannon with one big
> spell. If Darcy can drag the attacks aimed at Frank (or Michelle) onto himself and then
> evade them all with one action, Frank gets both actions to blow things up.

## Catcher

*Passive, Interrupt.* The presidential save — *Mr President, get down.*

- **When:** a direct hit (not an area attack) has *already succeeded* and is about to damage a mate next to you.
- **Move:** you can take a 10-foot step to get next to them first.
- **Effect:** you take the damage instead. You can't evade it, shield-block it or magic it away.
- **Rank 5:** +5 DR whenever you catch, then another +5 at 10 and 15. A dedicated catcher becomes very hard to hurt.
- **The catch:** it's a Passive skill, and you can't use one without ranks. Neither of you has it yet. Passive skills usually come from a potion, a scroll or gear.

**Taunt or Catcher?** Taunt happens *before* the dice. You redirect the attack and can still
dodge it. Catcher happens *after* the hit lands. You just take it, but it can't fail.

## Other passives to watch for

You can't attempt passive skills untrained, so these only matter once loot, a potion or a
scroll gives you a rank. If one turns up, here's why you'd want it.

- **[[skill-dodge|Dodge]]** — +1 to every Evade. At rank 15 evading doesn't cost an action. Good for both of you.
- **[[skill-aiming|Aiming]]** — ranged only. Take Disadvantage to add your Aiming rank to hit, and +1d4 damage. Darcy.
- **[[skill-double-tap|Double Tap]]** — declare it before the GM signposts, then spend both actions attacking one target. If the first shot is Amazing, the second one (if it hits) becomes a crit. Darcy.
- **[[skill-zone-of-control|Zone of Control]]** — needs a reach weapon. Hit anything that steps next to you.
- **[[skill-regeneration|Regeneration]]** — heal a health slot every round, or every other round.

## How well did it go?

The GM tells you the result, not the target number.

- **Natural 20 — Critical:** attack rolls double the damage dice. A crit on an Evade gives you Advantage on your next attack against that mob.
- **Beat it by 10+ — Amazing:** attacks do bonus damage equal to the floor number (+1 on Floor 1). Evades give Advantage on your next attack against that mob.
- **Beat it by 0–9 — Standard:** it worked.
- **Miss by 1–2 — Near Miss:** the GM calls it out. Someone Intervene, now.
- **Miss by 3–9 — Standard Fail:** the attack misses, or the evade fails and you get hit.
- **Miss by 10+ — Major Fail:** the attack goes wrong (drop it, need a reload). A failed evade takes bonus damage equal to the floor number, plus a Minor Injury after the fight.
- **Natural 1 — Critical Fail:** the worst outcome. A failed evade takes double damage, plus a Major Injury after the fight.

## Taking damage

Take off your **DR** first. Then knock out health slots. You have ten slots. Mark one off
for each full slot's worth of damage, and throw away whatever's left over that doesn't fill
a slot.

Frank has 2 health per slot and 1 DR. A boomerang hit for 6 becomes 5 after his DR. That's
two slots gone, and the last point is lost.

## Easy to forget

- **Untrained → Disadvantage.** Roll two d20s and take the lower. Trying anyway ticks the skill.
- **Hidden → Advantage.** Frank's first Magic Missile came from behind cover.
- **Hotlist your stuff.** Ten slots. Anything not on it costs an action to dig out. The spell, the shotgun and the potions belong there.
- **Mana doesn't come back mid-fight.** Only rest, potions or a buff will do it.
- **Mobs:** ordinary mobs get a move and one attack each, split evenly across the party. Bosses and elites get one action *per crawler*.
- **[[call-a-play]]** is a beat 4 action. 2d6, keep the highest, add it to your mate's roll — or to the damage, if they'd have hit anyway.
