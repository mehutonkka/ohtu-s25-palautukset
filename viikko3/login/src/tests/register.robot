*** Settings ***
Resource  resource.robot
Suite Setup     Open And Configure Browser
Suite Teardown  Close Browser
Test Setup      Reset Application Create User And Go To Register Page

*** Test Cases ***

Register With Valid Username And Password
    Click Link  Register new user
    Set Username  newuser1
    Set Password  ValidPass123
    Set Password Confirmation  ValidPass123
    Click Button  Register
    Register Should Succeed
    Go To Starting Page

Register With Too Short Username And Valid Password
    Click Link  Register new user
    Set Username  ne
    Set Password  ValidPass123
    Set Password Confirmation  ValidPass123
    Click Button  Register
    Register Should Fail with Message  Username must be at least 3 characters long
    Go To Starting Page

Register With Valid Username And Too Short Password
    Click Link  Register new user
    Set Username  newuser2
    Set Password  Vali1
    Set Password Confirmation  Vali1
    Click Button  Register
    Register Should Fail with Message  Password must be at least 8 characters long
    Go To Starting Page

Register With Valid Username And Invalid Password
# salasana ei sisällä halutunlaisia merkkejä
    Click Link  Register new user
    Set Username  newuser3
    Set Password  Validpassword
    Set Password Confirmation  Validpassword
    Click Button  Register
    Register Should Fail with Message  Password must contain at least one number
    Go To Starting Page

Register With Nonmatching Password And Password Confirmation
    Click Link  Register new user
    Set Username  ne2
    Set Password  ValidPass123
    Set Password Confirmation  NonValidPass123
    Click Button  Register
    Register Should Fail with Message  Password and password confirmation do not match
    Go To Starting Page

Register With Username That Is Already In Use
    Click Link  Register new user
    Set Username  existinguser
    Set Password  ValidPass123
    Set Password Confirmation  ValidPass123
    Click Button  Register
    Register Should Fail with Message  User with username existinguser already exists
    Go To Starting Page

*** Keywords ***
Login Should Succeed
    Main Page Should Be Open

Login Should Fail With Message
    [Arguments]  ${message}
    Login Page Should Be Open
    Page Should Contain  ${message}

Set Username
    [Arguments]  ${username}
    Input Text  username  ${username}

Set Password
    [Arguments]  ${password}
    Input Password  password  ${password}

Set Password Confirmation
    [Arguments]  ${password_confirmation}
    Input Password  password_confirmation  ${password_confirmation}

Register Should Succeed
    Title Should Be  Welcome to Ohtu Application!

Register Should Fail with Message
    [Arguments]  ${message}
    Register Page Should Be Open
    Page Should Contain  ${message}


*** Keywords ***
Reset Application Create User And Go To Register Page
    Reset Application
    Create User  existinguser  ExistingPass123
    Go To Starting Page