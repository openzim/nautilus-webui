require('dap').configurations.python = {
    {
        name = 'Launch FastAPI Server',
        type = 'python',
        request = 'launch',
        -- cwd = "${workspaceFolder}/src",
        -- module = "uvicorn",
        -- args = { "src.main:app", "--reload" },
        program = vim.fn.getcwd() .. "/src/backend/entrypoint.py",
        env = {
            PYTHONPATH = vim.fn.getcwd() .. "/src",
        },
        pythonPath = function()
            return 'python'
        end,
    },
}
