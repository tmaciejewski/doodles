module Main where

data Token = BinaryOp (Integer -> Integer -> Integer) | Num Integer

rpnEval :: [Token] -> Integer
rpnEval = rpnEval' [] where 
		rpnEval' (i:stack) [] = i
		rpnEval' stack ((Num i):tokens) = rpnEval' (i:stack) tokens
		rpnEval' (a:b:stack) ((BinaryOp op):tokens) = rpnEval' ((op a b):stack) tokens
		rpnEval' _ _ = error "Bad syntax"	 


toToken :: String -> Token
toToken "+" = BinaryOp (+)
toToken "-" = BinaryOp (-)
toToken "*" = BinaryOp (*)
toToken "/" = BinaryOp div
toToken s = Num (read s)

toTokens = map toToken

main = interact (unlines . map (show . rpnEval . toTokens . words) . lines)
