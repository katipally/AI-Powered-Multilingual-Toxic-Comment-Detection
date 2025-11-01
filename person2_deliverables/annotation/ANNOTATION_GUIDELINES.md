# Annotation Guidelines: Toxic Comment Detection

**Version:** 1.0 
**Date:** 2025-10-30 
**Target IAA:** Cohen's κ ≥ 0.70 

---

## Overview

This document provides guidelines for annotating comments as **toxic (1)** or **non-toxic (0)**, and optionally identifying toxicity subtypes.

### Core Principle
> **Toxicity is harmful content that attacks, threatens, insults, or harasses individuals or groups based on identity or characteristics.**

---

## Binary Classification

### Toxic (1) - Mark as toxic if comment contains:

1. **Hate Speech**
 - Attacks based on race, religion, gender, sexual orientation, disability, nationality
 - Dehumanizing language (e.g., "these people are animals")
 - Incitement to violence or discrimination

2. **Threats**
 - Direct or indirect threats of violence
 - Threats of harm to person or property
 - Death threats

3. **Severe Insults/Profanity**
 - Profanity directed at a person or group
 - Severe personal attacks
 - Derogatory slurs (consider context)

4. **Harassment**
 - Repeated targeting of individuals
 - Cyberbullying behavior
 - Stalking-like behavior

5. **Self-Harm Promotion**
 - Encouraging suicide or self-harm
 - Providing methods for self-harm

### Non-Toxic (0) - Mark as non-toxic if:

1. **Constructive Criticism**
 - Points out flaws without personal attacks
 - Professional disagreement
 - Policy or idea critique

2. **Strong Opinions (Non-Targeting)**
 - Political views without targeting individuals
 - General complaints about systems
 - Disagreement with ideas (not people)

3. **Mild Profanity (Context-Dependent)**
 - Casual profanity without targeting (e.g., "This is so f***ing frustrating")
 - Cultural expressions (e.g., "yaar", "bhenchod" used casually among friends)

4. **Sarcasm/Jokes**
 - Obvious sarcasm indicators (/s, emoji, LOL)
 - Self-deprecating humor
 - Jokes without malicious intent

5. **Quotes/Reproduction**
 - Quoting toxic content while clearly condemning it
 - Reporting on toxic content

---

## Toxicity Subtypes (Multi-Label)

If a comment is **toxic**, select **all applicable** subtypes:

### 1. Hate (`hate`)
- Attacks based on identity (race, religion, gender, etc.)
- **Example:** "All [group] are criminals and should be deported"
- **Not:** General political disagreement

### 2. Threat (`threat`)
- Threats of physical violence or harm
- **Example:** "I will find you and hurt you"
- **Not:** Warnings about consequences (e.g., "you'll be banned")

### 3. Insult (`insult`)
- Severe personal attacks, profanity directed at person/group
- **Example:** "You're an idiot and you know nothing"
- **Not:** Mild criticism ("I disagree with your point")

### 4. Harassment (`harassment`)
- Repeated targeting, cyberbullying patterns
- **Example:** Multiple comments targeting same person
- **Note:** Usually identified across multiple comments

### 5. Self-Harm (`self_harm`)
- Encouraging suicide or self-harm
- **Example:** "Just kill yourself already"
- **Note:** If present, prioritize for immediate action

---

## Code-Mixed Text Considerations

### Romanized Hindi (Hinglish)

**Context Matters!**

- **Toxic:** "bhenchod, teri maa ki..." (direct insult)
- **Toxic:** "chutiya government" (direct profanity)
- **Non-Toxic:** "yaar, kya baat hai" (casual/friendly)
- **Non-Toxic:** "bhai, this is good" (friendly address)

**Guidelines:**
- If profanity is directed at a person/group → **Toxic**
- If profanity is casual/exclamatory → Context-dependent (usually non-toxic)
- Common Hindi words (yaar, bhai, hai, nahi) are **not** toxic

### Mixed Language Patterns

- If comment mixes languages but meaning is clear, annotate based on meaning
- If unclear, mark confidence as "low" and add notes

---

## Edge Cases

### 1. Reclaimed Slurs
- **Context:** Who is using the term?
- **Toxic if:** Used by outsider to target group
- **Non-toxic if:** Self-identified member of group using reclaimed term
- **Uncertain:** Mark confidence "low" and add note

### 2. Sarcasm
- Look for indicators: `/s`, emoji (😂, 😏), "LOL", exaggerated language
- **Toxic if:** Sarcasm masks actual attack
- **Non-toxic if:** Clearly satirical without harm intent

### 3. Quotes
- **Toxic if:** Endorsing or repeating without condemnation
- **Non-toxic if:** Clearly quoting to critique (e.g., "They said X, which is terrible")

### 4. Political Discourse
- **Toxic if:** Personal attacks, identity-based attacks
- **Non-toxic if:** Policy critique, disagreement with ideas
- **Example Toxic:** "All [party] voters are stupid"
- **Example Non-Toxic:** "This policy is flawed because..."

### 5. Historical References
- **Toxic if:** Used to justify current attacks
- **Non-toxic if:** Educational/historical discussion

### 6. Self-Deprecation
- Generally **non-toxic** unless encouraging harm to self

---

## Confidence Levels

### High
- Clear toxic/non-toxic decision
- Follows guidelines directly
- No ambiguity

### Medium
- Generally clear but some nuance
- Minor context uncertainty
- Standard cases

### Low
- Edge case or ambiguous
- Requires interpretation
- Cultural context unclear
- **Action:** Add notes for review

---

## Annotation Process

1. **Read the entire comment** carefully
2. **Check for context** (subreddit, video title in metadata)
3. **Determine binary label** (0 or 1)
4. **If toxic:** Select all applicable subtypes
5. **Optional:** Highlight toxic phrases (rationale)
6. **Set confidence level**
7. **Add notes** if uncertain or edge case

---

## Quality Checks

### Self-Check Before Submitting

- [ ] Binary label is clear (0 or 1)
- [ ] If toxic: At least one subtype selected
- [ ] Confidence level reflects certainty
- [ ] Notes added for edge cases
- [ ] No obvious mistakes

### Common Mistakes to Avoid

- Marking sarcasm as toxic
- Marking strong opinions as toxic
- Missing code-mixed context
- Forgetting to select subtypes for toxic comments
- Not adding notes for ambiguous cases

---

## Examples

### Example 1: Clear Toxic
**Text:** "You're a disgusting piece of trash and should be banned from this platform"

- **Label:** Toxic (1)
- **Subtypes:** Insult
- **Confidence:** High
- **Notes:** Direct personal attack

### Example 2: Clear Non-Toxic
**Text:** "I disagree with this policy because it doesn't address the root causes"

- **Label:** Non-Toxic (0)
- **Confidence:** High
- **Notes:** Constructive criticism

### Example 3: Edge Case (Sarcasm)
**Text:** "Oh yeah, that's a brilliant idea 😏 /s"

- **Label:** Non-Toxic (0)
- **Confidence:** Medium
- **Notes:** Sarcasm with clear indicators

### Example 4: Code-Mixed (Casual)
**Text:** "Yaar, this movie is so good! Kya baat hai bhai"

- **Label:** Non-Toxic (0)
- **Confidence:** High
- **Notes:** Friendly Hindi-English mix, no targeting

### Example 5: Code-Mixed (Toxic)
**Text:** "Tum sab chutiye ho, ghar jaao"

- **Label:** Toxic (1)
- **Subtypes:** Insult
- **Confidence:** High
- **Notes:** Direct insult in Hinglish

### Example 6: Threat
**Text:** "I know where you live and I'm coming for you"

- **Label:** Toxic (1)
- **Subtypes:** Threat
- **Confidence:** High
- **Notes:** Direct threat of violence

---

## Disagreement Resolution

If annotators disagree:

1. **Review both annotations**
2. **Check guidelines** for relevant section
3. **Consider context** (metadata, surrounding comments)
4. **Adjudicator decides** based on guidelines
5. **Update guidelines** if pattern emerges

---

## Questions?

For unclear cases:
1. Check this document first
2. Check examples above
3. Mark confidence "low" and add detailed notes
4. Ask annotator lead for guidance

---

**Last Updated:** 2025-10-30 
**Next Review:** After pilot annotation round

