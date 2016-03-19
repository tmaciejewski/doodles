import sys
import operator

def maxCommonSuffix(word1, word2):
    i = len(word1) - 1
    j = len(word2) - 1
    suffixLen = 0

    while i >= 0 and j >= 0 and word1[i] == word2[j]:
        i -= 1
        j -= 1
        suffixLen += 1
    
    if suffixLen > 0:
        return word1[-suffixLen:]
    else:
        return ''

if len(sys.argv) != 3:
    print 'Usage:'
    print '\t', sys.argv[0], 'wordsFile word'
    print
    print '\twordsFile -- eg. /usr/share/dict/words'
    sys.exit(1)

wordsFile = open(sys.argv[1])
word = sys.argv[2]

vowels = 'aeyuio'

rhymes = []

for line in wordsFile:
    dictWord = line.strip() 
    suffix = maxCommonSuffix(word, dictWord)
    if dictWord != word and len(suffix) > 1:
        if suffix[-1] in vowels:
            suffix = suffix[:-1]

        level = sum(suffix.count(c) for c in vowels)
        if level > 0:
            rhymes.append((dictWord, level))

rhymes.sort(key=operator.itemgetter(1), reverse=True)

for rhyme, level in rhymes:
    print rhyme, level
