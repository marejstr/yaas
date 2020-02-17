# Report

## Full name and student number at Åbo Akademi

Martin Rejström, 31783

## List of implemented requirements

I had problem with the tests and decided to program only for the requirements

List over implemented requirements:

* UC1: create user
* UC2: edit user
* UC3: create auction(no test provided, verified manually)
* UC4: edit auction description
* UC5: Browse & Search
* UC6: bid
* UC7: ban auction
* UC8: resolve auction
* UC9: language switching
* UC10: concurrency(no test provided, verified manually)
* UC11: currency exchange
* REQ9.3: store language preference
* REQ3.5: send seller auction link
* WS1: Browse & Search API
* WS2: Bid api
* TREQ4.2:  implement data generation program  (verified manually)
* TREQ4.1.1 test REQ9.3(verified manually)

Not implemented requirements:

* TREQ4.1.2 test for REQ3.5(verified manually)
* TREQ4.1.3: test for REQ10.1 (verified manually)

## Browser and IDE

To test the application i used Firefox 70.0 (64-bit) on Fedora Linux

I did not use the suggested PyCode IDE. Instead I used Visual Studio Code. Hopefully it does not present any problems.

## Python packages

* Django==2.2.5
* requests==2.22.0
* djangorestframework==3.10.2
* freezegun==0.3.12
