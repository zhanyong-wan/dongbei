#include "Parser.h"
void MiniParser::run() {
    while (peek().type != TokenType::END_OF_FILE) {
        if (peek().type == TokenType::IDENTIFIER) {
            parseVarOrAssign();
        }
        else if (peek().type == TokenType::KW_SAY) {
            parseSay();
        }
        else {
            consume();
        }
    }
}
void MiniParser::parseVarOrAssign() {
    std::string name = consume().value; // 拿到变量名

    if (peek().type == TokenType::KW_BE) {
        // 解析：老王 是 [规整] 活雷锋。
        consume(); // 是
        if (consume().type == TokenType::TYPE_INT) {
            consume(); // 活雷锋
            consume(); // 。
            std::cout << "int " << name << ";" << std::endl;
        }
    }
    else if (peek().type == TokenType::KW_BECOME) {
        // 解析：老王 装 250 加 250。
        consume(); // 装
        std::string val1 = consume().value;
        if (peek().type == TokenType::KW_PLUS) {
            consume(); // 加
            std::string val2 = consume().value;
            consume(); // 。
            std::cout << name << " = " << val1 << " + " << val2 << ";" << std::endl;
        }
    }
}
void MiniParser::parseSay() {
    consume(); // 唠唠
    consume(); // ：
    std::string name = consume().value;
    consume(); // 。
    std::cout << "std::cout << " << name << " << std::endl;" << std::endl;
}