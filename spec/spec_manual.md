# Headspace Android App - Manual Functional Requirements Specification
**Project:** Headspace Android (com.getsomeheadspace.android)
**Pipeline Stage:** Manual (Task 3.3)
**Source:** personas_manual.json (P1-P5), derived from review groups G1-G5
**Dataset:** reviews_clean.jsonl (4,538 reviews)

---

# Requirement ID: FR1

- **Description:** The system shall display full subscription pricing information, including all available plan tiers, costs, and billing frequencies, before prompting the user to create an account or begin onboarding.
- **Source Persona:** P1 - Locked-Out Subscriber
- **Traceability:** Derived from review group G1 (Subscription paywall and pricing complaints)
- **Acceptance Criteria:**
  - Given a new user opens the app for the first time,
  - When the app loads its initial screen,
  - Then the user must be able to view all available subscription plans and their prices without entering any personal information or creating an account.

---

# Requirement ID: FR2

- **Description:** The system shall not charge the user's payment method until the advertised free trial period has fully elapsed, and must display a clear countdown of the remaining trial days within the app.
- **Source Persona:** P1 - Locked-Out Subscriber
- **Traceability:** Derived from review group G1 (Subscription paywall and pricing complaints)
- **Acceptance Criteria:**
  - Given a user has started a free trial,
  - When the user opens the app during the trial period,
  - Then the app must display the number of remaining trial days prominently, and no payment must be processed until the trial period ends without cancellation.

---

# Requirement ID: FR3

- **Description:** The system shall send the user an in-app notification at least 72 hours before any subscription renewal or price change, allowing the user to cancel or review billing before the charge is applied.
- **Source Persona:** P1 - Locked-Out Subscriber
- **Traceability:** Derived from review group G1 (Subscription paywall and pricing complaints)
- **Acceptance Criteria:**
  - Given a user's subscription is due to renew or the subscription price has changed,
  - When the renewal or price change date is within 72 hours,
  - Then the system must display an in-app notification and, if permissions allow, a push notification informing the user of the upcoming charge and the new amount.

---

# Requirement ID: FR4

- **Description:** The system shall not crash, freeze, or terminate abnormally during an active meditation, sleep cast, or focus audio session. If an unrecoverable error occurs, the system must save the user's session progress and resume from the last known position upon restart.
- **Source Persona:** P2 - Disrupted Meditator
- **Traceability:** Derived from review group G2 (App crashes and performance degradation)
- **Acceptance Criteria:**
  - Given a user has started and is actively listening to a meditation or sleep cast session,
  - When the session is between 10% and 100% complete,
  - Then the application must not crash or freeze; and if a crash does occur, upon reopening the app must offer to resume the session from the point of interruption.

---

# Requirement ID: FR5

- **Description:** The system shall load to a playable state (i.e., audio session ready to start) within 5 seconds of the user tapping a session, when measured on a device with an active internet connection of at least 4G/LTE speed.
- **Source Persona:** P2 - Disrupted Meditator
- **Traceability:** Derived from review group G2 (App crashes and performance degradation)
- **Acceptance Criteria:**
  - Given a user with an active LTE or Wi-Fi connection taps on any meditation, sleep cast, or focus session,
  - When the session loading screen appears,
  - Then the audio must begin playing or be ready to play within 5 seconds; if the load time exceeds 5 seconds, the system must display a visible loading indicator explaining the delay.

---

# Requirement ID: FR6

- **Description:** The system shall complete the login flow entirely within the app. When using OAuth-based authentication (e.g., Google Sign-In), the system must redirect back to the app automatically after browser-based authentication completes, without requiring the user to manually reopen the app.
- **Source Persona:** P3 - Authentication-Blocked Returner
- **Traceability:** Derived from review group G3 (Login and account access failures)
- **Acceptance Criteria:**
  - Given a user selects "Sign in with Google" (or any supported OAuth provider),
  - When the external authentication step completes successfully in the browser,
  - Then the system must automatically return focus to the Headspace app and log the user in without requiring any additional manual action; the login loop must not repeat.

---

# Requirement ID: FR7

- **Description:** The system shall restore an existing user's account, subscription status, and historical session data when the user installs the app on a new or different Android device and signs in with the same credentials.
- **Source Persona:** P3 - Authentication-Blocked Returner
- **Traceability:** Derived from review group G3 (Login and account access failures)
- **Acceptance Criteria:**
  - Given a user has an active account and subscription on one device,
  - When the user installs the Headspace app on a different Android device and signs in with identical credentials,
  - Then the system must restore the user's subscription entitlements, streak data, and previously accessed content without prompting account re-creation or showing an empty profile.

---

# Requirement ID: FR8

- **Description:** The system shall display a specific, actionable error message when authentication fails due to a third-party account link (e.g., employer benefit, NHS, or insurance provider), indicating the exact cause of failure and the steps required to resolve it.
- **Source Persona:** P3 - Authentication-Blocked Returner
- **Traceability:** Derived from review group G3 (Login and account access failures)
- **Acceptance Criteria:**
  - Given a user attempts to authenticate via a third-party benefit provider (e.g., Cigna, NHS),
  - When the authentication attempt fails for any reason,
  - Then the system must display an error message that identifies the specific failure reason (e.g., "Your benefit plan could not be verified. Please contact your provider.") and must not display a generic message such as "Oops, something went wrong."

---

# Requirement ID: FR9

- **Description:** The system shall provide a persistent, keyword-based search function across the full content library (meditations, sleep casts, courses, and focus tracks) accessible from the app's primary navigation bar.
- **Source Persona:** P4 - Navigation-Frustrated Subscriber
- **Traceability:** Derived from review group G4 (Poor UI design and content navigation difficulty)
- **Acceptance Criteria:**
  - Given a user is on any screen within the app,
  - When the user taps the search icon in the navigation bar and enters a keyword (e.g., "anxiety", "sleep", "10 minutes"),
  - Then the system must return a filtered list of relevant content items from across all content categories within 2 seconds, ranked by relevance.

---

# Requirement ID: FR10

- **Description:** The system shall display any in-progress course or programme on the home screen in a clearly labelled "Continue" section, showing the user's completion percentage and the next session to be completed.
- **Source Persona:** P4 - Navigation-Frustrated Subscriber
- **Traceability:** Derived from review group G4 (Poor UI design and content navigation difficulty)
- **Acceptance Criteria:**
  - Given a user has started but not completed a guided course or multi-session programme,
  - When the user navigates to the home screen,
  - Then the system must display a "Continue" or equivalent section listing all in-progress content with the title, the percentage completed, and a direct tap target to resume the next session.

---

# Requirement ID: FR11

- **Description:** The system shall allow users to filter the sleep cast and meditation libraries by at least the following attributes: session duration, topic or focus area (e.g., sleep, anxiety, stress, focus), and instructor name.
- **Source Persona:** P4 - Navigation-Frustrated Subscriber
- **Traceability:** Derived from review group G4 (Poor UI design and content navigation difficulty)
- **Acceptance Criteria:**
  - Given a user is browsing the sleep cast or meditation library,
  - When the user opens the filter panel,
  - Then the system must present filter options for at minimum: duration range, topic or focus category, and instructor; and applying any filter must update the displayed content list immediately without requiring a full page reload.

---

# Requirement ID: FR12

- **Description:** The system shall track and display the user's total cumulative minutes meditated and current daily streak, updating these figures immediately upon completion of any session, and surfacing them on the home screen without requiring navigation to a separate profile page.
- **Source Persona:** P5 - Committed Wellness Practitioner
- **Traceability:** Derived from review group G5 (Positive mindfulness and mental wellness experience)
- **Acceptance Criteria:**
  - Given a user completes a meditation, sleep cast, or focus session,
  - When the session end screen is displayed,
  - Then the system must show the updated total minutes meditated and the current streak count on the session completion screen; and both figures must also be visible on the home screen the next time the user returns to it, without additional navigation.

---

# Requirement ID: FR13

- **Description:** The system shall update its personalised content recommendations based on the user's session history, explicitly rated content, and stated wellness goals, refreshing recommendations at least once every 7 days to reflect evolving usage patterns.
- **Source Persona:** P5 - Committed Wellness Practitioner
- **Traceability:** Derived from review group G5 (Positive mindfulness and mental wellness experience)
- **Acceptance Criteria:**
  - Given a user has completed at least 5 sessions or rated at least 3 content items,
  - When the user opens the app's home or discover screen,
  - Then the system must display a personalised recommendation section whose content differs meaningfully from the generic new-user default, reflecting the user's session history and stated preferences; and this recommendation set must update at least once per 7-day period if the user has been active.

---

# Requirement ID: FR14

- **Description:** The system shall provide a free tier that includes a minimum of 10 distinct guided meditation sessions accessible without a subscription, allowing new users to evaluate core functionality before committing to payment.
- **Source Persona:** P1 - Locked-Out Subscriber
- **Traceability:** Derived from review group G1 (Subscription paywall and pricing complaints)
- **Acceptance Criteria:**
  - Given an unauthenticated user or a user who has not started a free trial,
  - When the user browses the content library,
  - Then the system must make at least 10 complete, distinct guided meditation sessions available to play without requiring subscription sign-up, and each such session must be clearly labelled as "Free."

---
