Feature: Changing Password

  Scenario: User wants to change their password.
    Given user is logged in
      And the user’s current password is “password”
      And the user has entered a new password - “NEWPASSWORD”
      And the user has entered a confirmation password - “NEWPASSWORD”
      And the two password inputs are identical
    When the user submits the password change
    Then the user’s password be “NEWPASSWORD”
 
  Scenario: User wants to change their password.
    Given user is logged in
      And the user’s current password is “password”
      And the user has entered a new password - “NEWPASSWORD”
      And the user has entered a confirmation password - “NeWpAsSwOrD”
      And the two password inputs are different
    When the user submits the password change
    Then the user’s password be “password”
      And the UI should display a relevant  error message
 
 
Feature: Accepting Invite

  Scenario: User has been invited to an event and must accept the invitation.
    Given user is logged in
      And they have been added as a guest to another user’s event
    Then the user is given a notification that prompts the user to accept the invite
    When the user accepts the invite
    Then the event appears on their event list

    
Feature: Displaying Event Feed

  Scenario: User wants to view events
    Given the user is logged in
      And the user is on home page
    Then the bottom left corner displays the public events
      And the user can scroll through events
    When user selects “Sort by: most recent”
    Then the events are displayed in order of date with the most recent at the top
    When the user selects “Sort by: alphabet”
    Then the events are displayed in alphabetical order
	
  
Feature: Search by Name

  Scenario: User wants to find an event by searching for its name
    Given user is logged in
      And user is on home page
      And the user has selected the search bar
    When the user enters in a name of an event or part of a name
    Then any matching events should display below
