from features import analyze_url, analyze_email, calculate_score, visualize_result

def main():
    print("=== PhishShield: Intelligent Phishing Detection System ===")
    user_input = input("Enter URL or Email Text: ")

    if "http" in user_input or "www" in user_input:
        features = analyze_url(user_input)
    else:
        features = analyze_email(user_input)

    score, verdict = calculate_score(features)


    print(f"\n Verdict: {verdict}")
    print(f"\n Risk score: {score}%") 

    visualize_result(features,score,verdict)

if __name__ == "__main__" :
    main()   



