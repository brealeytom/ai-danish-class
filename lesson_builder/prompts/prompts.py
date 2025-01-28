

types_of_segment = ['Immersion','Shadowing','ConversationalPractice','ActiveListening','ErrorCorrection','Role-Playing','SpacedRepetition']

targetphrases = ['Hvad hedder du?','Jeg hedder Tom'...]
recapphrases = ['et','to','tre'...]
if segment = 'Immersion' then 
prompt = '
#role 
*fill in this here*

#task
*fill in this here*

#example input
*fill in here*

#example output
*fill in here*

#target words

#validation requirements
'

print prompt