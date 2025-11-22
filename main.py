from features import (
    analyze_url,
    analyze_email,
    predict_email_ml,
    calculate_score,
    visualize_result
)

def main():
    print("========================================")
    print("        🛡️  PhishShield v1.0            ")
    print("   AI-Powered Phishing Detection Tool   ")
    print("========================================\n")

    #User Input """Fixes User's Multiline input for email"""
    
    print("Enter email text (press ENTER twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "":                  
            break
        lines.append(line)

    user_input = "\n".join(lines)


    # Decide if input is URL or Email
    if "http://" in user_input or "https://" in user_input or "www" in user_input:
        input_type = "url"
        print("\nDetected Input Type: URL\n")

        # URL → Heuristic analysis only
        features = analyze_url(user_input)
        ml_prob = 0.0   # No ML for URLs

    else:
        input_type = "email"
        print("\nDetected Input Type: Email Text\n")

        # EMAIL → Heuristics + ML model
        features = analyze_email(user_input)
        ml_prob = predict_email_ml(user_input)

    # Final hybrid score
    final_score, verdict = calculate_score(features, ml_prob, input_type)

    # Display results
    print("============ RESULT ============\n")
    print(f"ML Probability of Phishing : {round(ml_prob * 100, 2)}%")
    print(f"Final Risk Score           : {round(final_score, 2)}%")
    print(f"Verdict                    : {verdict}")

    # Save visualization
    print("\nGenerating risk visualization chart...")
    visualize_result(features, final_score, verdict)
    print("Chart saved in: screenshots/risk_chart.png")

    print("\n========================================")
    print("        Scan complete. Stay safe!        ")
    print("========================================")

if __name__ == "__main__":
    main()
