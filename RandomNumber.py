import random

def guess_the_number():
    print("Welcome to 'Guess the Number'!")
    print("The computer will randomly select a number between 1 and 100.")
    print("Your task is to guess the number.")
    
    # The computer randomly selects a number between 1 and 100
    number_to_guess = random.randint(1, 10)
    
    # Initialize the number of guesses
    number_of_guesses = 0
    
    while True:
        # Prompt the player to enter a guess
        try:
            player_guess = int(input("Enter your guess: "))
        except ValueError:
            print("Please enter a valid integer.")
            continue
        
        # Increment the number of guesses
        number_of_guesses += 1
        
        # Check if the player's guess is correct
        if player_guess < number_to_guess:
            print("Too low! Try again.")
        elif player_guess > number_to_guess:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You've guessed the number in {number_of_guesses} tries.")
            break

# Start the game
guess_the_number()

