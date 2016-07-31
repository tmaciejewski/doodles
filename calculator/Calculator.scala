object Calculator {
    def main(args: Array[String]): Unit = {
        val line = io.StdIn.readLine()
        if (line != null) {
            val tokens = line.split("\\s+") map (parseToken)
            val rpnForm = toRPN(tokens.toList)
            println(evalRPN(rpnForm))
            main(args)
        }
    }

    trait Token

    trait BinaryOp extends Token {
        def priority: Int
        def fun(x: Int, y: Int): Int
    }

    object Add extends BinaryOp {
        def priority = 2
        def fun(x: Int, y: Int) = x + y
        override def toString = "+"
    }

    object Sub extends BinaryOp {
        def priority = 2
        def fun(x: Int, y: Int) = x - y
        override def toString = "-"
    }
    object Mul extends BinaryOp {
        def priority = 1
        def fun(x: Int, y: Int) = x * y
        override def toString = "*"
    }
    object Div extends BinaryOp {
        def priority = 1
        def fun(x: Int, y: Int) = x / y
        override def toString = "/"
    }
    case class Number(value: Int) extends Token {
        override def toString = value.toString
    }

    def parseToken(token: String): Token = token match {
        case "+" => Add
        case "-" => Sub
        case "*" => Mul
        case "/" => Div
        case number => Number(number.toInt)
    }

    def toRPN(tokens: List[Token], opers: List[BinaryOp] = List(), output: List[Token] = List()): List[Token] = tokens match {
        case Nil => output.reverse ++ opers
        case (number: Number) :: otherTokens  => toRPN(otherTokens, opers, number :: output)
        case (oper: BinaryOp) :: otherTokens  => {
            val (newOpers, newOutput) = addOper(oper, opers, output)
            toRPN(tokens.tail, newOpers, newOutput)
        }
        case _ :: otherTokens  => toRPN(otherTokens, opers, output)
    }

    def addOper(oper: BinaryOp, opers: List[BinaryOp], output: List[Token]): (List[BinaryOp], List[Token]) = {
        if (opers.isEmpty || opers.head.priority > oper.priority)
            (oper :: opers, output)
        else
            addOper(oper, opers.tail, opers.head :: output)
    }

    def evalRPN(tokens: List[Token], stack: List[Int] = List()): Int = tokens match {
        case Nil => stack.head
        case (number: Number) :: otherTokens => evalRPN(otherTokens, number.value :: stack)
        case (oper: BinaryOp) :: otherTokens => {
            val arg2 = stack.head
            val arg1 = stack.tail.head
            val res = oper.fun(arg1, arg2)
            evalRPN(otherTokens, res :: stack.tail.tail)
        }
        case _ :: otherTokens => evalRPN(otherTokens, stack)
    }
}
