#include "Parser.h" 

int main() {
    // 模拟源码：老王 是 [规整] 活雷锋。老王 装 250 加 250。唠唠：老王。
    std::vector<Token> testTokens = {
        {TokenType::IDENTIFIER, "laowang"}, {TokenType::KW_BE, ""}, {TokenType::TYPE_INT, ""}, {TokenType::KW_IS_VAR, ""}, {TokenType::KW_PERIOD, ""},
        {TokenType::IDENTIFIER, "laowang"}, {TokenType::KW_BECOME, ""}, {TokenType::NUMBER, "250"}, {TokenType::KW_PLUS, ""}, {TokenType::NUMBER, "250"}, {TokenType::KW_PERIOD, ""},
        {TokenType::KW_SAY, ""}, {TokenType::KW_COLON, ""}, {TokenType::IDENTIFIER, "laowang"}, {TokenType::KW_PERIOD, ""}
    };

    MiniParser parser(testTokens);
    parser.run();

    return 0;
}