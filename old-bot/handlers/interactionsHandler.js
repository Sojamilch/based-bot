/**
 * @param {Object} client
 * @param {String} filePath
 * @returns {void}
 */
const fs = require('node:fs');
const path = require('node:path');
const handleInteractions = (client, filePath) => {
    //const slashCommands = fs.readdirSync(`${filePath}/commands`);


    const commandsPath = path.join(filePath, 'commands');
    const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

    for (const file of commandFiles) {
    	const filePath = path.join(commandsPath, file);
    	const command = require(filePath);
    	// Set a new item in the Collection with the key as the command name and the value as the exported module
    	if ('data' in command && 'execute' in command) {
    		client.slashCommands.set(command.data.name, command);
    	} else {
    		console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
    	}
    }


    // for (const module of slashCommands) {
    //     const commandFiles = fs
    //         .readdirSync(`${filePath}\\commands\\${module}`)
    //         .filter((file) => file.endsWith(".js"));

    //     for (const commandFile of commandFiles) {
    //         const command = require(`${filePath}/commands/${module}/${commandFile}`);
    //         client.slashCommands.set(command.data.name, command);
    //     }
    // }

};
module.exports = handleInteractions;