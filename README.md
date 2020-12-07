# Tombola

Weihnachtstombolaspiel

Spiel zur Ziehung der Weihnachtstombola für eXXcellent solutions

Code and music copyright David Jenkins, 2020, except works by Dark Fantasy Studio, copyright Nicolas Jeudy / DARK FANTASY STUDIO 

All rights reserved 


#Input
Parameter 
```
-i file
```
Pfad zur Excel Datei, die die Namen und Lose enthält. e.g.

```
python adventure.py -i "../eXXcellent/Weihnachtsfeier/TombolaLose.xlsx
```
The format of the Excel is very simple. Two columns, headed `Name` and `Lose` hold the name to display
for the player, and the number of lives they have (= number of tickets, i.e. Lose, they bought)

![img.png](img.png)

#Output

File **winners.txt** contains the list of winners

#If things go wrong

```
( All settings in adventure.py)
```

Parameter 
```
MOVEMENT_SPEED = 5
```

controls Mabel's speed. If everybody buys lots of lives, then it may be advisable to speed up Mabel to get through the game quicker.

If only 15 coins appear, debug mode is set. Check function
```
is_debug()
```
to see if it has been set to permanently return true.