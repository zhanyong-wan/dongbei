#pragma once
#include <string>
#include <unordered_map>
#include <utility>
#include <memory>
#include <iostream>

enum class TokenType {
    IDENTIFIER,     // 老王
    NUMBER,         // 250
    KW_BE,          // 是
    TYPE_INT,       // [规整]
    KW_IS_VAR,      // 活雷锋
    KW_BECOME,      // 装
    KW_PLUS,        // 加
    KW_SAY,         // 唠唠
    KW_COLON,       // ：
    KW_PERIOD,      // 。
    END_OF_FILE
};

inline std::vector<std::pair<std::string, TokenType>> dongbei_keywords = {
    {"是活雷锋", TokenType::KW_IS_VAR},
    {"嘀咕", TokenType::KW_SAY},
    {"装", TokenType::KW_BECOME},
    {"加", TokenType::KW_PLUS},
    {"。", TokenType::KW_PERIOD},
    {"：", TokenType::KW_COLON}
};