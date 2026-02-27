#pragma once
#include "Keywords.h"
struct Token {
    TokenType type;
    std::string value; // 比如 "100" 或者 "老王"
};
class Node {
public:
    virtual ~Node() = default;
    // 核心：转译成 C++ 代码的逻辑
    virtual std::string to_cpp() const = 0;
};
class VariableNode : public Node {
    std::string name;
public:
    VariableNode(std::string n) : name(std::move(n)) {}
    std::string to_cpp() const override {
        return name; // 假设 dongbei 变量名直接兼容 C++，否则得做个映射
    }
};
class NegateNode : public Node {
    std::unique_ptr<Node> operand;
public:
    NegateNode(std::unique_ptr<Node> op) : operand(std::move(op)) {}
    std::string to_cpp() const override {
        // 加个括号保平安，防止运算优先级整串了
        return "(-(" + operand->to_cpp() + "))";
    }
};
class BinaryNode : public Node {
    TokenType op;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;
public:
    BinaryNode(TokenType o, std::unique_ptr<Node> l, std::unique_ptr<Node> r)
        : op(o), left(std::move(l)), right(std::move(r)) {
    }

    std::string to_cpp() const override {
        std::string op_str;
        switch (op) {
        case TokenType::KW_PLUS:       op_str = "+"; break;
        //case TokenType::KW_MINUS:      op_str = "-"; break;
        //case TokenType::KW_TIMES:      op_str = "*"; break;
        //case TokenType::KW_DIVIDE_BY:  op_str = "/"; break;
        //case TokenType::KW_EQUAL:      op_str = "=="; break;
        default: op_str = " /* 啥玩意儿 */ ";
        }
        // 生成形如 (left + right) 的代码
        return "(" + left->to_cpp() + " " + op_str + " " + right->to_cpp() + ")";
    }
};
class NumberNode : public Node {
    std::string value;
public:
    NumberNode(std::string v) : value(std::move(v)) {}
    std::string to_cpp() const override {
        return value;
    }
};
struct VarDeclNode : Node {
    std::string name;
    std::string cpp_type; // 映射自 [规整] -> int
    VarDeclNode(std::string n, std::string t) : name(n), cpp_type(t) {}
    std::string to_cpp() const override { return cpp_type + " " + name + ";"; }
};
// 赋值语句：老王 装 表达式
struct AssignNode : Node {
    std::string var_name;
    std::string expr_cpp;
    AssignNode(std::string n, std::string e) : var_name(n), expr_cpp(e) {}
    std::string to_cpp() const override { return var_name + " = " + expr_cpp + ";"; }
};

// 打印语句：唠唠：表达式
struct SayNode : Node {
    std::string expr_cpp;
    SayNode(std::string e) : expr_cpp(e) {}
    std::string to_cpp() const override { return "std::cout << " + expr_cpp + " << std::endl;"; }
};
class MiniParser {
    std::vector<Token> tokens;
    int pos = 0;

    Token peek() { return (pos < tokens.size()) ? tokens[pos] : Token{ TokenType::END_OF_FILE }; }
    Token consume() { return tokens[pos++]; }

public:
    MiniParser(std::vector<Token> t) : tokens(t) {}
    void run();
private:
    void parseVarOrAssign();
    void parseSay();
};