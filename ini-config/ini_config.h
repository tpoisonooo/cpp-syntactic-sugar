#pragma once
#include <string>
#include <unordered_map>
#include <vector>
#include <fstream>
#include <memory>
#include <sstream>
#include <type_traits>
#include <cassert>

// ini format table reader and writer
// file example:
//
// [Conv_0]
// type = "Conv"
// input_scale = 127.0
// weight = [ 1117.265625, 8819.232421875 ]
//
// [LayerNorm_66]
// type = "LayerNorm"
// zero_point = -24

namespace ini
{

template<typename T>
std::string value_set(T data) {
    return std::to_string(data);
}

template<>
std::string value_set<std::string>(std::string data) {
    return "\"" + data + "\"";
}

template<>
std::string value_set<const char*>(const char* data) {
    return "\"" + std::string(data) + "\"";
}

template<typename T>
std::string value_set(const std::vector<T>& data) {
    std::string  text = "[ ";
    size_t len = data.size();
    if (len > 0) {
        size_t i = 0;
        for (;i < len - 1; ++i) {
            text += std::to_string(data[i]);
            text += ", ";
        }
        text += std::to_string(data[i]);
        text += " ";
    }
    text += "]";
    return text;
}

template<typename T>
T value_get(std::string text) {
    T result;
    std::stringstream ss;
    ss << text;
    ss >> result;
    return result;
}

template<>
std::string value_get<std::string>(std::string text) {
    auto start = text.find("\"");
    auto end = text.find("\"");

    return text.substr(start+1, end);
}

template<typename T>
std::vector<T> value_get_list(std::string text) {
    std::vector<T> result;

    std::string no_brace;
    {
        // remove brace
        auto start = text.find('[');
        auto end = text.find(']');
        no_brace = text.substr(start + 1, end);
    }

    {
        // split with the separator ','
        std::stringstream ss;
        size_t end = 0, start = 0;
        while(true) {
            end = no_brace.find(',', start);
            if (end == std::string::npos){
                break;
            }

            std::string val_str = no_brace.substr(start, end);
            start = end + 1;

            T val;
            ss << val_str;
            ss >> val;
            ss.clear();
            result.emplace_back(val);
        }

        // parse the last one
        std::string val_str = no_brace.substr(start);
        T val;
        ss << val_str;
        ss >> val;
        result.emplace_back(val);
    }
    return result;
}

class Table {
public:
    Table() {}

    void feed(std::string line) {
        auto pos = line.find('=');
        assert(pos != std::string::npos);

        std::string key = line.substr(0, pos-1);
        std::string value_str = line.substr(pos+2);
        
        values[key] = value_str;
    }

    void feed(const std::vector<std::string>& lines) {
        for (auto& line : lines) {
            feed(line);
        }
    }

    std::string operator[](std::string key) {
        return values[key];
    }

    template<typename T>
    T get(std::string key) {
        std::string text = values[key];
        return value_get<T>(text);
    }

    template<typename T>
    std::vector<T> get_list(std::string key) {
        std::string text = values[key];
        return value_get_list<T>(text);
    }

    template<typename T>
    void append(std::string key, T data) {
        values[key] = value_set(data);
    }

    template<typename T>
    void append(std::string key, const std::vector<T>& data) {
        values[key] =value_set(data);
    }

    std::string stringify() {
        std::string result;
        for (auto itra = values.begin(); itra != values.end(); ++itra) {
            result += itra->first;
            result += " = ";
            result += itra->second;
            result += '\n';
        }
        return result;
    }

private:
    std::unordered_map<std::string, std::string> values;
};

class Config {
public:
    Config() {}

    void read(std::string path) {
        std::ifstream fin;
        fin.open(path, std::ios::in);

        if (! fin.is_open()) {
            fprintf(stderr, "open %s failed\n", path.c_str());
            return;
        }

        std::shared_ptr<Table> pTable = nullptr;
        constexpr int BUF_LEN = 1024 * 1024;
        char buf[BUF_LEN] = {0};
        std::string line;
        while(!fin.eof()) {
            fin.getline(buf, BUF_LEN);
            line = std::string(buf);

            if (line.length() <= 2) {
                pTable = nullptr;
                continue;;
            }

            if (nullptr == pTable) {
                auto start = line.find('[');
                auto end = line.find(']');
                assert(start != std::string::npos);
                assert(end != std::string::npos);

                std::string key = line.substr(start+1, end-1);

            fprintf(stderr, "readline %s,key %s\n", line.c_str(), key.c_str());

                pTable = std::make_shared<Table>();
                tables[key] = pTable;
                continue;
            } 

            pTable->feed(line);
        }
    }

    std::vector<std::string> list_all() {
        std::vector<std::string> result;
        for (auto itra = tables.begin(); itra != tables.end(); ++itra) {
            result.push_back(itra->first);
        }
        return result;
    }

    std::shared_ptr<Table> operator[](std::string key) {
        return tables[key];
    }

    void append(const std::string key, std::shared_ptr<Table> table) {
        tables[key] = table;
    }

    void write(const std::string path) {
        std::ofstream fout;
        fout.open(path, std::ios::out);
        if(! fout.is_open()) {
            fprintf(stderr, "open %s failed\n", path.c_str());
        }

        for (auto itra = tables.begin(); itra != tables.end(); ++itra){
            fout << "[" << itra->first << "]\n";
            fout << itra->second->stringify();
            fout << "\n";
        }
        fout.flush();
        fout.close();
    }

private:
    std::unordered_map<std::string, std::shared_ptr<Table> > tables;
};

} // namespace ini
