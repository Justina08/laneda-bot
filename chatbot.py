def handle_message(user_message):
    user_message = user_message.lower()

    if user_message in ['hi', 'hello', 'hey']:
        return ("👋 Welcome to *Laneda SmartTech*! We power business growth with AI tools.\n\n"
                "Please choose an option:\n1️⃣ Learn about our services\n2️⃣ Lead generation help\n"
                "3️⃣ Build a WhatsApp bot\n4️⃣ Talk to an agent\n5️⃣ Something else")

    if user_message == "1":
        return ("🌟 At Laneda SmartTech, we offer:\n- 🧠 AI Lead Generation\n- 🤖 WhatsApp Chatbots\n"
                "- 🧩 Workflow Automation\n- 💼 AI Consulting\n\nReply YES to proceed or MENU to return.")

    if user_message == "2":
        return ("🚀 Let's generate leads! Answer a few questions:\n1. Your business name & industry?\n"
                "2. Who is your ideal customer?\n3. What product/service do you offer?\n"
                "4. Do you have a customer list or want new leads?")

    if user_message == "3":
        return ("⚙️ Let’s build your bot! Please answer:\n1. Business name?\n"
                "2. What should the bot do? (e.g., answer FAQs, take orders)\n"
                "3. Should it connect to your CRM or website?\n4. Do you want full setup or DIY support?")

    if user_message == "4":
        return "👩‍💼 Please hold on. A team member will join shortly."

    if user_message == "5":
        return "🙋 Please type how I can help. I’ll do my best to assist or connect you with someone."

    return "🤖 Sorry, I didn't understand that. Please choose an option 1–5."
