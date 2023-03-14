import re

# character class to identify individual characters in lexical analysis
class characters:
    SPECIAL = 0
    DIGIT = 1
    UPPERCASE = 2
    LOWERCASE = 3
    UNKNOWN = 99
    @classmethod 
    def alphanumeric(self, char):
        return char == self.DIGIT or char == self.UPPERCASE or char == self.LOWERCASE        

# tokens class to enumerate tokens
class tokens:
    CHARACTER = 4
    STRING = 5
    NUMERAL = 6
    ALPHANUMERIC = 7
    CHARACTERLIST = 8
    VARIABLE = 9
    SMALLATOM = 10
    ATOM = 12
    SINGLEQUOTE = 13
    STRUCTURE = 14
    LEFTPAREN = 15
    RIGHTPAREN = 16
    TERM = 17
    TERMLIST = 18
    COMMA = 19
    PREDICATE = 20
    PREDICATELIST = 21
    QUESTIONMARKDASH = 22
    DOT = 23
    QUERY = 24
    CLAUSE = 25
    COLONDASH = 26
    CLUASELIST = 27
    QUESTIONMARK = 28
    COLON = 29
    DASH = 30
    UNKNOWN = 100
    EOF = 404


# lookup table for special characters
def Lookup(char):
    global nextToken
    if char == "(":
        addChar()
        nextToken = tokens.LEFTPAREN
    elif char == ")":
        addChar()
        nextToken = tokens.RIGHTPAREN
    elif char == "'":
        addChar()
        nextToken = tokens.SINGLEQUOTE
    elif char == ",":
        addChar()
        nextToken = tokens.COMMA
    elif char == "?":
        addChar()
        nextToken = tokens.QUESTIONMARK
    elif char == "-":
        addChar()
        nextToken = tokens.DASH
    elif char == ".":
        addChar()
        nextToken = tokens.DOT
    elif char == ":":
        addChar()
        nextToken = tokens.COLON
    elif char == "":
        addChar()
        nextToken = tokens.EOF
    else:
        addChar()
        nextToken = tokens.UNKNOWN
    return nextToken


def addChar():  # adds nextchar into string array lexeme, done this way so comments and whitespaces dont get passed
    global lexeme
    lexeme += nextChar


def getChar():  # gets next character from input and determines a character class
    global nextChar
    global charClass
    global lineNo
    nextChar = file.read(1)
    if nextChar.isalpha() or nextChar == "_":
        if nextChar.islower():
            charClass = characters.LOWERCASE
        else:
            charClass = characters.UPPERCASE
    elif nextChar.isdigit():
        charClass = characters.DIGIT
    elif re.search(r"[+\-*\/\\^~:.? $&]", nextChar):
        charClass = characters.SPECIAL
    else:
        charClass = characters.UNKNOWN


# keep parsing until we get a non-whitespace (i.e., r'\S') character
def getNonBlank():
    global nextChar
    global lineNo
    while str.isspace(nextChar):
        # parsing new line character increments
        # line counter
        if nextChar == "\n":
            lineNo += 1
        getChar()

# lexical analyzer
# parses until we get a non-whitespace character
# then the lexeme is tokenized
def lex():
    getNonBlank()
    global charClass
    global lexeme
    lexeme = ""
    global nextToken
    if charClass == characters.DIGIT:
        addChar()
        getChar()
        while charClass == characters.DIGIT: # checks for recursion
            addChar()
            getChar()
        nextToken = tokens.NUMERAL
    elif charClass == characters.UPPERCASE:
        addChar()
        getChar()
        while characters.alphanumeric(charClass): # checks for recursion
            addChar()
            getChar()
        nextToken = tokens.VARIABLE
    elif charClass ==  characters.LOWERCASE:
        addChar()
        getChar()
        while characters.alphanumeric(charClass): # checks for recursion
            addChar()
            getChar()
        nextToken = tokens.SMALLATOM
    elif charClass ==  characters.UNKNOWN:
        Lookup(nextChar)
        getChar()
        if nextToken == tokens.SINGLEQUOTE: # checks if its a string
            addChar()
            getChar()
            while (
                characters.alphanumeric(charClass)
                or charClass == characters.SPECIAL
            ):
                addChar()
                getChar()
            if nextToken == tokens.SINGLEQUOTE: # checks ending apostrophe
                addChar()
                getChar()
                nextToken = tokens.STRING

    elif charClass ==  characters.SPECIAL:
        Lookup(nextChar)
        getChar()
        # tries to tokenize for a COLONDASH
        if nextToken == tokens.COLON:
            Lookup(nextChar)
            if nextToken == tokens.DASH:
                getChar()
                nextToken = tokens.COLONDASH
        # tries to tokenize for a QUESTIONMARKDASH
        elif nextToken == tokens.QUESTIONMARK:
            Lookup(nextChar)
            if nextToken == tokens.DASH:
                getChar()
                nextToken = tokens.QUESTIONMARKDASH
    if nextToken == tokens.SMALLATOM or nextToken == tokens.STRING:
        nextToken = tokens.ATOM

# starting point of syntax analyzer
# checks if file contains a valid program
def program():
    global nextToken
    if nextToken == tokens.QUESTIONMARKDASH: # checks faster than clause-list query
        query()
    else:
        clauseList()
        query() # returns to execute a query after a clauseList is done

# checks if it is a query
def query():
    global nextToken
    global lineNo
    global erroneous
    global outFile
    if nextToken == tokens.QUESTIONMARKDASH: # if we find a query tag
        lex() # get next token
        predicateList() # check for following predicate list
        if nextToken != tokens.DOT: # check for ending .
            outFile.write(f"Error missing . of query at line {lineNo}\n") # register the error
            erroneous += 1
    else:
        outFile.write(f"Error missing ?- of quert at line {lineNo}\n") # register error
        erroneous+=1
        lex() # get next token
        predicateList() # check for following predicate list
        if nextToken != tokens.DOT: # check for ending .
            outFile.write(f"Error missing . of query at line {lineNo}\n") # register the error
            erroneous += 1

# checks if it is a clause-list
def clauseList():
    global nextToken
    global lineNo
    global erroneous
    global outFile
    if nextToken != tokens.ATOM: # error check if an atom isn't there
        outFile.write(f"Error missing atom of clause-list at line {lineNo}\n") # register the error
        erroneous += 1
    while nextToken != tokens.EOF and nextToken == tokens.ATOM: # While we have atoms to build a clause of the list
        clause() # call clause
        if nextToken == tokens.QUESTIONMARKDASH: # check if the end of a clause list was reached
            break # break out of the while loop
        lex() # get the next token

# checks if it is a clause
def clause():
    global nextToken
    global lineNo
    global erroneous
    global outFile
    predicate() # call predicate
    if nextToken == tokens.COLONDASH: # if the following lexeme is :-
        lex() # get the next token
        while nextToken != tokens.EOF and nextToken != tokens.DOT: # as long as the end of the clause isn't reached
            predicateList() # get the predicate list
        if nextToken != tokens.DOT and nextToken == tokens.QUESTIONMARKDASH: # if a ?- is found instead of a .
            outFile.write( # register the error
                f"Error missing . of clause's predicate list at line {lineNo}\n"
            )
            erroneous += 1
    elif nextToken != tokens.DOT: # otherwise no . or :- was found after the predicate
        erroneous += 1
        outFile.write( # register the error
                f"Error missing . or :- of clause at line {lineNo}\n"
            )
        # while we dont find a ?- or . or :-    
        while nextToken != tokens.EOF and (nextToken != tokens.QUESTIONMARKDASH or nextToken != tokens.DOT or nextToken != tokens.COLONDASH):
            if nextToken == tokens.QUESTIONMARKDASH or nextToken == tokens.EOF: # if we found a ?-
                outFile.write( # register the error
                    f"Error missing ."
                )
                break
            elif nextToken == tokens.DOT: # otherwise we found a .
                lex()
                break
            elif nextToken == tokens.COLONDASH: # otherwise we found a :-
                lex() # get the next token
                while nextToken != tokens.EOF and nextToken != tokens.DOT: # as long as the end of the clause isn't reached
                    predicateList() # get the predicate list
                if nextToken != tokens.DOT and nextToken == tokens.QUESTIONMARKDASH: # if a ?- is found instead of a .
                    outFile.write( # register the error
                        f"Error missing . of clause's predicate list at line {lineNo}\n"
                    )
                    erroneous += 1
                break
            lex()

# checks if it is a predicate
def predicate():
    global nextToken
    global lineNo
    global erroneous
    global outFile
    if nextToken == tokens.ATOM: # if we got an atom token
        lex() # get the next token
        if nextToken == tokens.LEFTPAREN: # if it is a left parenthesis
            lex() # get the next token
            termList() # check if it has a one or more comma-separated terms
            if nextToken == tokens.RIGHTPAREN: # if we got a right parenthesis
                lex() # get the next token to continue
            else: # if we don't get a matching parenthesis
                outFile.write( # register the error
                    f"Error missing right parenthesis of predicate at line {lineNo}\n"
                )
                erroneous += 1
                while nextToken != tokens.EOF and ( # consume the erroneous data till we find a proper part of the predicate
                    nextToken != tokens.COMMA
                    or nextToken != tokens.RIGHTPAREN
                    or nextToken != tokens.DOT
                ):
                    if nextToken == tokens.COMMA: # if we found a comma
                        lex() # get the next token
                        termList() # continue the term list
                        if nextToken == tokens.RIGHTPAREN:
                            lex()
                            break
                        else:
                            outFile.write( # register the error
                                f"Error missing right parenthesis of predicate at line {lineNo}\n"
                            )
                            erroneous += 1
                            break
                    elif nextToken == tokens.RIGHTPAREN: # if we found a right parenthesis
                        lex() # get the next token
                        break # exit to finish the predicate
                    elif nextToken == tokens.DOT: # if we found a .
                        break # exit to finish the predicate and assume there was a
                              # matching parenthesis to check remaining program
                    elif nextToken == tokens.QUESTIONMARKDASH: # if we found a ?-
                        break # exit and assume we found a matching parenthesis and .
                    elif nextToken == tokens.EOF:
                        break # exit
                    lex() # otherwise get the next token
    else: # otherwise we didn't find an atom
        while nextToken not in (tokens.DOT, tokens.COMMA, tokens.EOF): # loop till we get one of the previous
            lex() # get the next token
        outFile.write(f"Error missing atom predicate at line {lineNo}\n") # register the error
        erroneous += 1

# checks if it is a predicate-list
def predicateList():
    global nextToken
    predicate() # check for the first predicate of the list
    while nextToken != tokens.EOF and nextToken == tokens.COMMA: # while we have commas to separate
        lex() # get the next token
        predicate() # check for more predicates

# checks if it is a term-list
def termList():
    global nextToken
    term() # check for the first term of the list
    while nextToken != tokens.EOF and nextToken == tokens.COMMA: # while we have commas to separate
        lex() # get the next token
        term() # check for more terms

# checks if it is a term
def term():
    global nextToken
    global lineNo
    global erroneous
    global outFile
    if nextToken == tokens.ATOM: # if we found an atom
        lex() # get the next token
        if nextToken == tokens.LEFTPAREN: # check if there is a left parenthesis for a structure
            lex() # get the next token
            termList() # check if it has one or more terms in the list
            if nextToken == tokens.RIGHTPAREN: # if there is a matching parenthesis
                lex() # get the next token
            else: # otherwise
                outFile.write( # register the error
                    f"Error missing right parenthesis of term at line {lineNo}\n"
                )
                erroneous += 1
    elif nextToken == tokens.VARIABLE: # variable case
        lex() # get the next token
    elif nextToken == tokens.NUMERAL: # numeral case
        lex() # get the next token
    else: # non-terms
        lex() # get the next token
        while nextToken not in ( # until we find a
            tokens.EOF, # end of file,
            tokens.DOT,  # dot,
            tokens.COMMA, # comma,
            tokens.LEFTPAREN, # left parenthesis,
            tokens.RIGHTPAREN, # right parenthesis,
            tokens.COLONDASH, # :-,
            tokens.QUESTIONMARKDASH, # or ?-
        ):
            lex() # keep tokenizing
        else:
            outFile.write(f"Error no matching term at line {lineNo}\n") # register the error
            erroneous += 1

# driver
def main():
    fileNum = 1
    try:
        while True:
            global lineNo
            global file
            global erroneous
            file = open(f"{fileNum}.txt", "r") # open the next file for reading
            outFile.write(f"Program {fileNum}.txt:\n") # output the name of the file in the output file
            # driver code
            getChar() 
            lex()
            program()
            lineNo = 1 # reset number of lines
            fileNum += 1 # reset number of files
            file.close() # close the input file
            if erroneous == 0: # if the program had no errors
                outFile.write(f"Program ran correctly!\n")
            else: 
                outFile.write(f"Program ended with {erroneous} error{'s'*(erroneous>1)}\n")
            outFile.write(
                f"-------------------------------------------------------------------------------------------\n\n"
            )
            erroneous = 0 # reset number of errors

    except FileNotFoundError: # to check for the end of text files in the relative path
        outFile.close()

reachedEnd = False
lexeme = ""  # string variable to hold lexeme
outFile = open("parser_output.txt", "w") # outputs errors/lack of errors to file
nextChar = "" # stores next character
charClass = 99
nextToken = 0 # stores next token
lineNo = 1 # keeps track of file line numbers
erroneous = 0 # boolCheck to detect if program had errors
main() # this is the main