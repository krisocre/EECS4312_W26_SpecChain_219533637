# Headspace Android App - Hybrid Functional Requirements Specification
**Project:** Headspace: Mindful Meditation (com.getsomeheadspace.android)
**Pipeline Stage:** Hybrid
**Source:** personas/personas_hybrid.json (5 personas), revised from the automated pipeline outputs
**Dataset:** data/reviews_clean.jsonl (4,538 reviews)

---

# Requirement ID: FR_hybrid_1

- **Description:** The system shall display subscription plans, prices, billing frequency, and free-trial terms before requiring account creation or payment details.
- **Source Persona:** P_hybrid_1 - Price-Conscious Explorer
- **Traceability:** Derived from review group H1 (Pricing clarity and usable free access)
- **Acceptance Criteria:**
  - Given a first-time user opens the app,
  - When the onboarding or subscribe screen appears,
  - Then the app must show all available plans, prices, billing intervals, and trial terms before the user is asked to create an account or enter payment information.

---

# Requirement ID: FR_hybrid_2

- **Description:** The system shall provide at least 10 complete guided meditation sessions that can be played without a subscription and without entering payment information.
- **Source Persona:** P_hybrid_1 - Price-Conscious Explorer
- **Traceability:** Derived from review group H1 (Pricing clarity and usable free access)
- **Acceptance Criteria:**
  - Given a user has not started a paid subscription or free trial,
  - When the user browses the meditation library,
  - Then the app must clearly label and allow playback of at least 10 full guided meditation sessions without a paywall or payment prompt.

---

# Requirement ID: FR_hybrid_3

- **Description:** The system shall allow an active meditation, sleep cast, or focus session to continue without crashing, freezing, or stopping unexpectedly during playback.
- **Source Persona:** P_hybrid_2 - Interrupted Daily Listener
- **Traceability:** Derived from review group H2 (Playback failures and app instability)
- **Acceptance Criteria:**
  - Given a user has started an audio session,
  - When the session is between 10% and 100% complete,
  - Then the app must continue playback without an unexpected crash, freeze, or stop event.

---

# Requirement ID: FR_hybrid_4

- **Description:** The system shall load a selected meditation or sleep session to a playable state within 5 seconds on a supported device with an active Wi-Fi or LTE connection, or show a visible loading indicator until playback is ready.
- **Source Persona:** P_hybrid_2 - Interrupted Daily Listener
- **Traceability:** Derived from review group H2 (Playback failures and app instability)
- **Acceptance Criteria:**
  - Given a supported Android device with an active Wi-Fi or LTE connection,
  - When the user selects a meditation or sleep session,
  - Then the session must begin playing within 5 seconds or the app must display a visible loading indicator until playback is ready.

---

# Requirement ID: FR_hybrid_5

- **Description:** The system shall complete OAuth-based sign-in by automatically returning focus to the app and authenticating the user without repeating the login prompt.
- **Source Persona:** P_hybrid_3 - Locked-Out Subscriber
- **Traceability:** Derived from review group H3 (Login recovery and subscription restoration)
- **Acceptance Criteria:**
  - Given a user selects a supported OAuth sign-in option,
  - When the external authentication step succeeds,
  - Then the app must regain focus automatically and sign the user in without showing the login screen again.

---

# Requirement ID: FR_hybrid_6

- **Description:** The system shall restore an existing user's subscription entitlements, previously accessed content, and progress data when the user signs in on a new Android device with the same account.
- **Source Persona:** P_hybrid_3 - Locked-Out Subscriber
- **Traceability:** Derived from review group H3 (Login recovery and subscription restoration)
- **Acceptance Criteria:**
  - Given a user has an existing account with active subscription access on one device,
  - When the user signs in on a second Android device with the same account,
  - Then the app must restore the user's paid access and previously recorded progress without asking the user to create a new profile.

---

# Requirement ID: FR_hybrid_7

- **Description:** The system shall provide a global keyword search from the primary navigation that returns relevant results from meditations, sleep casts, and courses within 2 seconds.
- **Source Persona:** P_hybrid_4 - Overwhelmed Navigator
- **Traceability:** Derived from review group H4 (Search, navigation, and resume friction)
- **Acceptance Criteria:**
  - Given a logged-in user is on a primary app screen,
  - When the user enters a keyword in the global search,
  - Then the app must return relevant cross-category results within 2 seconds and allow the user to open a result directly from the search results list.

---

# Requirement ID: FR_hybrid_8

- **Description:** The system shall display each in-progress course or program in a dedicated Continue section on the home screen, including the next session to resume and the completion percentage.
- **Source Persona:** P_hybrid_4 - Overwhelmed Navigator
- **Traceability:** Derived from review group H4 (Search, navigation, and resume friction)
- **Acceptance Criteria:**
  - Given a user has started but not completed at least one multi-session course or program,
  - When the user returns to the home screen,
  - Then the app must show each in-progress item in a Continue section with its title, percentage complete, and a direct action to resume the next session.

---

# Requirement ID: FR_hybrid_9

- **Description:** The system shall update and display the user's total minutes meditated and current streak immediately after a session ends and surface the same values on the home screen.
- **Source Persona:** P_hybrid_5 - Habit-Building Meditator
- **Traceability:** Derived from review group H5 (Progress tracking and routine support)
- **Acceptance Criteria:**
  - Given a user completes a meditation or sleep session,
  - When the session completion screen appears,
  - Then the app must show the updated total minutes meditated and current streak, and the same values must also be visible the next time the user opens the home screen.

---

# Requirement ID: FR_hybrid_10

- **Description:** The system shall allow a user to save a meditation or sleep item and access the saved item from a dedicated saved-content area within 2 navigation steps from the home screen.
- **Source Persona:** P_hybrid_5 - Habit-Building Meditator
- **Traceability:** Derived from review group H5 (Progress tracking and routine support)
- **Acceptance Criteria:**
  - Given a user is viewing a meditation or sleep item,
  - When the user saves the item,
  - Then the app must store it in a dedicated saved-content area and allow the user to reach that saved item within 2 navigation steps from the home screen.

---
