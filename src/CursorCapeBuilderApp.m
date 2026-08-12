#import <Cocoa/Cocoa.h>

@interface CapeAppDelegate : NSObject <NSApplicationDelegate>
@property (nonatomic) BOOL receivedOpenEvent;
@property (nonatomic) BOOL isProcessing;
@end

@implementation CapeAppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.4 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
        if (!self.receivedOpenEvent && !self.isProcessing) [self chooseSource];
    });
}

- (void)application:(NSApplication *)application openFiles:(NSArray<NSString *> *)filenames {
    self.receivedOpenEvent = YES;
    if (filenames.count == 1) [self generateFromPath:filenames.firstObject];
    else [self showError:@"一次只能转换一个 ZIP 或图片文件夹。"];
}

- (void)application:(NSApplication *)application openURLs:(NSArray<NSURL *> *)urls {
    self.receivedOpenEvent = YES;
    if (urls.count == 1) [self generateFromPath:urls.firstObject.path];
    else [self showError:@"一次只能转换一个 ZIP 或图片文件夹。"];
}

- (void)chooseSource {
    NSOpenPanel *panel = [NSOpenPanel openPanel];
    panel.title = @"选择原始光标 ZIP 或图片文件夹";
    panel.prompt = @"生成 Cape";
    panel.canChooseFiles = YES;
    panel.canChooseDirectories = YES;
    panel.allowsMultipleSelection = NO;
    if ([panel runModal] == NSModalResponseOK) {
        [self generateFromPath:panel.URL.path];
    } else {
        [NSApp terminate:nil];
    }
}

- (void)generateFromPath:(NSString *)sourcePath {
    if (self.isProcessing) return;
    self.isProcessing = YES;

    NSString *fileName = sourcePath.lastPathComponent;
    NSString *capeName = [[fileName.pathExtension lowercaseString] isEqualToString:@"zip"]
        ? [fileName stringByDeletingPathExtension] : fileName;
    NSString *outputPath = [[sourcePath.stringByDeletingLastPathComponent
        stringByAppendingPathComponent:[capeName stringByAppendingString:@" (自动生成).cape"]] stringByStandardizingPath];
    NSString *scriptPath = [[NSBundle mainBundle] pathForResource:@"CursorCapeBuilder" ofType:@"py"];
    NSString *pythonPath = @"/Library/Frameworks/Python.framework/Versions/3.13/bin/python3";
    if (![[NSFileManager defaultManager] isExecutableFileAtPath:pythonPath]) pythonPath = @"/usr/bin/python3";

    NSTask *task = [[NSTask alloc] init];
    task.launchPath = pythonPath;
    task.arguments = @[scriptPath, sourcePath, outputPath, @"--name", capeName];
    NSPipe *errorPipe = [NSPipe pipe];
    task.standardError = errorPipe;
    @try {
        [task launch];
        [task waitUntilExit];
    } @catch (NSException *exception) {
        self.isProcessing = NO;
        [self showError:[NSString stringWithFormat:@"无法启动生成器：%@", exception.reason]];
        return;
    }
    self.isProcessing = NO;

    if (task.terminationStatus != 0 || ![[NSFileManager defaultManager] fileExistsAtPath:outputPath]) {
        NSData *data = [errorPipe.fileHandleForReading readDataToEndOfFile];
        NSString *detail = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] ?: @"未知错误";
        [self showError:[NSString stringWithFormat:@"生成失败：\n%@", detail]];
        return;
    }

    [[NSWorkspace sharedWorkspace] activateFileViewerSelectingURLs:@[[NSURL fileURLWithPath:outputPath]]];
    NSUserNotification *notification = [[NSUserNotification alloc] init];
    notification.title = @"Cursor Cape Builder";
    notification.informativeText = [NSString stringWithFormat:@"已生成 %@", outputPath.lastPathComponent];
    [[NSUserNotificationCenter defaultUserNotificationCenter] deliverNotification:notification];
    [NSApp terminate:nil];
}

- (void)showError:(NSString *)message {
    NSAlert *alert = [[NSAlert alloc] init];
    alert.messageText = @"Cursor Cape Builder";
    alert.informativeText = message;
    [alert addButtonWithTitle:@"好"];
    [alert runModal];
}

@end

int main(int argc, const char * argv[]) {
    @autoreleasepool {
        NSApplication *application = [NSApplication sharedApplication];
        CapeAppDelegate *delegate = [[CapeAppDelegate alloc] init];
        application.delegate = delegate;
        [application setActivationPolicy:NSApplicationActivationPolicyRegular];
        return NSApplicationMain(argc, argv);
    }
}
