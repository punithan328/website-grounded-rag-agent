# # import chainlit as cl

# # from app.agent.graph import build_graph


# # # Build the graph once when the application starts.
# # graph = build_graph()


# # @cl.on_chat_start
# # async def on_chat_start():

# #     await cl.Message(
# #         content=(
# #             "# Website Grounded AI Assistant\n\n"
# #             "Ask me a question about the indexed "
# #             "website.\n\n"
# #             "I will answer only using information "
# #             "retrieved from the website."
# #         )
# #     ).send()


# # @cl.on_message
# # async def on_message(message: cl.Message):

# #     query = message.content.strip()

# #     if not query:
# #         await cl.Message(
# #             content="Please enter a question."
# #         ).send()

# #         return

# #     # ----------------------------------------
# #     # Run LangGraph
# #     # ----------------------------------------

# #     result = await cl.make_async(
# #         graph.invoke
# #     )(
# #         {
# #             "query": query,
# #             "retry_count": 0,
# #         }
# #     )

# #     final_response = result.get(
# #         "final_response",
# #         "I couldn't generate a response.",
# #     )

# #     await cl.Message(
# #         content=final_response
# #     ).send()

# import chainlit as cl

# from app.agent.graph import build_graph


# graph = build_graph()


# @cl.on_chat_start
# async def on_chat_start():

#     await cl.Message(
#         content=(
#             "Website-Grounded RAG Agent\n\n"
#             "Ask a question about the ChromaDB website."
#         )
#     ).send()


# @cl.on_message
# async def on_message(
#     message: cl.Message,
# ):
#     thinking = cl.Message(
#     content="Searching the indexed website..."
#     )

#     await thinking.send()
#     thinking.content = "Generating grounded answer..."
#     await thinking.update()

#     query = message.content.strip()

#     if not query:

#         await cl.Message(
#             content="Please enter a question."
#         ).send()

#         return

#     result = await cl.make_async(
#         graph.invoke
#     )(
#         {
#             "query": query,
#             "retry_count": 0,
#         }
#     )

#     answer = result.get(
#         "answer",
#         result.get(
#             "final_response",
#             "No answer generated.",
#         ),
#     )

#     grounded = result.get(
#         "grounded",
#         False,
#     )

#     sources = result.get(
#         "sources",
#         [],
#     )

#     # ----------------------------------------
#     # Answer
#     # ----------------------------------------

#     await cl.Message(
#         content=answer
#     ).send()

#     # ----------------------------------------
#     # Grounding status
#     # ----------------------------------------

#     if grounded:

#         await cl.Message(
#             content="**Grounded:** Yes"
#         ).send()

#     # ----------------------------------------
#     # Sources
#     # ----------------------------------------

#         if sources:
    
#             elements = []

#             for source in sources:

#                 elements.append(
#                     cl.Text(
#                         name=source.get(
#                             "title",
#                             "Source",
#                         ),
#                         content=source["url"],
#                         display="inline",
#                     )
#                 )

#             await cl.Message(
#                 content="### Sources",
#                 elements=elements,
#             ).send()

import chainlit as cl

from app.agent.graph import build_graph


graph = build_graph()


@cl.on_chat_start
async def on_chat_start():

    await cl.Message(
        content=(
            "# Website Grounded AI Assistant\n\n"
            "Ask a question about the indexed website."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):

    query = message.content.strip()

    if not query:
        await cl.Message(
            content="Please enter a question."
        ).send()
        return

    # ----------------------------------------
    # Retrieval Step
    # ----------------------------------------

    async with cl.Step(
        name="Retrieval",
        type="tool",
    ) as step:

        step.input = query

        result = await cl.make_async(
            graph.invoke
        )(
            {
                "query": query,
                "retry_count": 0,
            }
        )

        documents = result.get(
            "retrieved_documents",
            [],
        )

        step.output = (
            f"Retrieved {len(documents)} "
            f"documents."
        )

    # ----------------------------------------
    # Sources Step
    # ----------------------------------------

    sources = result.get(
        "sources",
        [],
    )

    if sources:

        async with cl.Step(
            name="Sources",
            type="tool",
        ) as step:

            source_lines = []

            for index, source in enumerate(
                sources,
                start=1,
            ):

                title = source.get(
                    "title",
                    "Source",
                )

                url = source.get(
                    "url",
                    "",
                )

                source_lines.append(
                    f"{index}. {title}\n"
                    f"{url}"
                )

            step.output = "\n\n".join(
                source_lines
            )

    # ----------------------------------------
    # Final Answer
    # ----------------------------------------

    answer = result.get(
        "answer",
        result.get(
            "final_response",
            "No answer generated.",
        ),
    )

    await cl.Message(
        content=answer
    ).send()