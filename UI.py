import streamlit as st
import requests
import time

API_BASE = "https://ai-pr-reviewer-production-3270.up.railway.app" 
#API_BASE = "http://localhost:8003" 


st.set_page_config(page_title="PR Analyzer", layout="centered")

st.title("🔍 GitHub PR Analyzer")

repo_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo")
pr_number = st.number_input("Pull Request Number", min_value=1, step=1)

if st.button("Analyze PR"):
    with st.spinner("Sending PR for analysis..."):
        response = requests.post(f"{API_BASE}/analyze-pr", json={
            "repo_url": repo_url,
            "pr_number": pr_number
        })
        if response.status_code == 429:
            st.error("Too many requests. Please wait a minute before trying again.")
            st.stop()

        elif response.status_code != 200:
            st.error(f"Failed to start analysis: {response.status_code} - {response.text}")
            st.stop()
        
        else:
            task_id = response.json().get("task_id")
            if not task_id:
                st.error("No task ID received.")
                st.stop()

            st.success(f"Task started! Task ID: {task_id}")
            start_time = time.time()

            with st.spinner("Waiting for analysis to complete..."):
                while True:
                    status_res = requests.get(f"{API_BASE}/status/{pr_number}")
                    status = status_res.json().get("status", "pending")

                    if status == "completed":
                        break
                    elif status == "failed":
                        st.error("Analysis failed.")
                        st.stop()
                    else:
                        time.sleep(2)

            result_res = requests.get(f"{API_BASE}/results/{pr_number}")
            if result_res.status_code != 200:
                st.error("Failed to fetch results.")
                st.stop()

            result = result_res.json()
            st.success("✅ Analysis Completed!")

            st.subheader("📋 Summary")
            st.json(result.get("summary", {}))

            st.subheader("📄 PR Info")
            st.write(f"Repo: {result.get('repo_url')}")
            st.write(f"PR Number: {result.get('pr_number')}")
            st.write(f"Diff Length: {result.get('length')} characters")

            end_time = time.time()
            elapsed_time = end_time - start_time
            st.success(f"Analysis completed in {elapsed_time:.2f} seconds!")
