import generator

from data import DATA
from config import TOKEN, LOG_FILE
from loguru import logger

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

class Bot:
    def __init__(self, token: str, log_filename: str):
        self.__init_logging(log_filename)
        self.__init_bot(token)


    def __init_logging(self, filename: str) -> None:
        logger.debug(f"Creating file log: {filename}")
        logger.add(filename, rotation="500 MB", serialize=True, 
                   format="{time:MMMM D, YYYY > HH:mm:ss!UTC} | {level} | {message}")
        
    def __init_bot(self, token: str) -> None:
        self.app = ApplicationBuilder().token(token).build()
        self.app.add_handler(CommandHandler("start", self.__start_handler))
        self.app.add_handler(CallbackQueryHandler(self.__create_new_handler, "CQ_CREATE_NEW"))
        self.app.add_handler(CallbackQueryHandler(self.__cancel_handler, "CQ_CANCEL"))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.__url_handler))

    async def __start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Command '/start' triggered id={id} username={username}", 
                    id=update.effective_chat.id, username=update.effective_chat.username)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=DATA["start"]["reply"], reply_markup=DATA["start"]["keyboard"])
        
    async def __create_new_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Callback query 'CQ_CREATE_NEW' triggered id={id} username={username}", 
                    id=update.callback_query.from_user.id, username=update.callback_query.from_user.username)
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text=DATA["create_new"]["reply"], reply_markup=DATA["create_new"]["keyboard"])
        context.user_data["expecting_message"] = True

    async def __url_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: 
        if context.user_data.get('expecting_message') == None:
            logger.warning("Context variable 'expecting_message' was not found id={id} username={username}", 
                    id=update.effective_chat.id, username=update.effective_chat.username)
            context.user_data['expecting_message'] = False
            return
        if context.user_data['expecting_message'] == False:
            return
        logger.info("Generating short URL id={id} username={username}",
                    id=update.effective_chat.id, username=update.effective_chat.username)
        url, err = generator.generate_url(update.message.text, update.effective_chat.id)
        if err != None:
            logger.warning("{message} id={id} username={username}", message=err,
                    id=update.effective_chat.id, username=update.effective_chat.username)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=str(err), reply_markup=DATA["create_new"]["keyboard"])
            return
        context.user_data['expecting_message'] = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text=url, reply_markup=DATA["start"]["keyboard"])
    
    async def __cancel_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Callback query 'CQ_CANCEL' triggered id={id} username={username}", 
                    id=update.callback_query.from_user.id, username=update.callback_query.from_user.username)
        if context.user_data.get('expecting_message') == None:
            logger.warning("Context variable 'expecting_message' was not found id={id} username={username}", 
                    id=update.effective_chat.id, username=update.effective_chat.username)
        context.user_data['expecting_message'] = False
        await update.callback_query.edit_message_text(text=DATA["start"]["reply"], reply_markup=DATA["start"]["keyboard"])

    def run(self):
        self.app.run_polling()

if __name__ == "__main__":
    Bot(TOKEN, LOG_FILE).run()